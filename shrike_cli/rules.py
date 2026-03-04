STRIPE_RULES = {
    # ─── Framework-Specific Webhook Rules ───
    "NEXTJS_APP_ROUTER_WEBHOOK_RAW_BODY_ERROR": {
        "regex_triggers": [
            r"No signatures found",
            r"route\.(?:ts|js)",
            r"App Router",
            r"req\.json\(\)"
        ],
        "severity": "CRITICAL",
        "base_confidence": 95,
        "root_cause": "Next.js App Router: `req.json()` consumes the stream. Stripe requires the raw body buffer.",
        "impact": "Webhook signatures will fail validation entirely.",
        "minimal_patch": "const body = await req.text(); // MUST extract raw text\nconst sig = headers().get('stripe-signature');",
        "verification_steps": ["[ ] Ensure req.text() is used instead of req.json()"]
    },
    "EXPRESS_WEBHOOK_SIGNATURE_VERIFICATION_FAILURE": {
        "regex_triggers": [
            r"No signatures found",
            r"express",
            r"body-parser"
        ],
        "severity": "CRITICAL",
        "base_confidence": 95,
        "root_cause": "Express.js: generic `express.json()` middleware executing before raw body capture.",
        "impact": "Webhook signatures will fail validation entirely.",
        "minimal_patch": "app.post('/webhook', express.raw({ type: 'application/json' }), ...)",
        "verification_steps": ["[ ] Use express.raw() only for the webhook endpoint."]
    },
    
    # ─── Layer 1: State Machine Integrity ───
    "PAYMENT_INTENT_REQUIRES_ACTION": {
        "regex_triggers": [
            r"(?i)(?:status|state)['\"\s:=]+requires_action",
            r"(?i)unhandled status[:\s]+requires_action",
            r"3d secure authentication required"
        ],
        "severity": "CRITICAL",
        "base_confidence": 96,
        "root_cause": "The backend failed to return the `client_secret` to frontend for SCA/3D Secure authentication.",
        "impact": "Payments stuck in incomplete state. Lost revenue.",
        "minimal_patch": "const { error, paymentIntent } = await stripe.handleCardAction(clientSecret);",
        "verification_steps": ["[ ] Check frontend handles 'requires_action' status by prompting user."]
    },
    "PAYMENT_METHOD_FAILURE_LOOP": {
        "regex_triggers": [
            r"(?i)requires_payment_method.*?retry attempt.*?requires_payment_method",
            r"(?i)requires_payment_method.*requires_payment_method"
        ],
        "severity": "HIGH",
        "base_confidence": 94,
        "root_cause": "PaymentIntent being reused after failure instead of creating new one or handling gracefully.",
        "impact": "Server looping, poor UX, possible Stripe rate limit hit.",
        "minimal_patch": "if (intent.status === 'requires_payment_method') {\n  // Do not retry blindly. Prompt for new card.\n}",
        "verification_steps": ["[ ] Break loops if card is permanently declined."]
    },
    "SUBSCRIPTION_STUCK_INCOMPLETE": {
        "regex_triggers": [
            r"(?i)invoice\.payment_failed.*incomplete",
            r"(?i)subscription status['\"\s:=]+incomplete"
        ],
        "severity": "HIGH",
        "base_confidence": 93,
        "root_cause": "Missing retry confirmation logic. Subscription created but first payment failed.",
        "impact": "Users think they subscribed but are stuck. No revenue collected.",
        "minimal_patch": "const invoice = await stripe.invoices.pay(invoice_id);\n// Verify payment intent status afterward",
        "verification_steps": ["[ ] Ensure frontend catches incomplete subscriptions and retries payment."]
    },
    
    # ─── Layer 2: Idempotency & Concurrency ───
    "WEBHOOK_IDEMPOTENCY_FAILURE": {
        "regex_triggers": [
            r"(?i)payment_intent\.succeeded.*timeout.*retry.*payment_intent\.succeeded",
            r"(?i)webhook processing failed.*duplicate key",
            r"(?i)already marked paid"
        ],
        "severity": "CRITICAL",
        "base_confidence": 98,
        "root_cause": "Missing event ID deduplication guard. Stripe retried a webhook because your server took too long (timeout), and your code processed the same event twice.",
        "impact": "Users double-credited, duplicate emails, duplicated business side-effects.",
        "minimal_patch": "const isProcessed = await db.exists(event.id);\nif (isProcessed) return res.status(200).send('Already processed');\nawait db.save(event.id);",
        "verification_steps": ["[ ] Store Stripe Event IDs in your DB and drop duplicates."]
    },
    "IDEMPOTENCY_KEY_NOT_ENFORCED": {
        "regex_triggers": [
            r"(?i)idempotency-key.*retry.*charge created again",
            r"(?i)duplicate charge.*same idempotency key"
        ],
        "severity": "CRITICAL",
        "base_confidence": 99,
        "root_cause": "Duplicate financial action. Idempotency key was logged or reused, but Stripe API was hit twice inappropriately without proper caching bounds.",
        "impact": "Customer charged twice for the same cart.",
        "minimal_patch": "// Use a robust caching layer to assign and retain idempotency keys per exact request payload hash.",
        "verification_steps": ["[ ] Ensure idempotency keys are regenerated if the order amount changes."]
    },
    "RACE_CONDITION_DUPLICATE_PAYMENT": {
        "regex_triggers": [
            r"(?i)frontend confirms.*webhook not yet.*original webhook arrives",
            r"(?i)new payment initiated.*webhook arrives"
        ],
        "severity": "CRITICAL",
        "base_confidence": 96,
        "root_cause": "Async Race: Frontend completes checkout while Webhook is still inflight. Application drops state or double-issues.",
        "impact": "Duplicate fulfillment or broken state machines.",
        "minimal_patch": "await db.transaction(async tx => {\n  const order = await tx.getOrder(orderId);\n  if (order.status === 'paid') return;\n  // process\n});",
        "verification_steps": ["[ ] Implement db-level locks (SELECT FOR UPDATE) on the order record."]
    },
    
    # ─── Layer 3: Database & Logic Boundaries ───
    "PARTIAL_TRANSACTION_COMMIT": {
        "regex_triggers": [
            r"(?i)payment_intent\.succeeded.*payments table success.*subscriptions table failed",
            r"(?i)write failed after payment success"
        ],
        "severity": "CRITICAL",
        "base_confidence": 97,
        "root_cause": "No transactional rollback. Payment was saved, but related entitlement (like subscription or user role) failed to write.",
        "impact": "Customer paid but didn't get their product. Database inconsistency.",
        "minimal_patch": "BEGIN;\nINSERT INTO payments ...;\nINSERT INTO subscriptions ...; -- if this fails, roll back\nCOMMIT;",
        "verification_steps": ["[ ] Wrap all post-payment database logic in atomic transactions block."]
    },
    "POST_PAYMENT_FULFILLMENT_FAILURE": {
        "regex_triggers": [
            r"(?i)payment_intent\.succeeded.*application logic error.*user role not upgraded"
        ],
        "severity": "HIGH",
        "base_confidence": 92,
        "root_cause": "Stripe succeeded perfectly, but internal application logic crashed before updating the user role or entitlement.",
        "impact": "Service not rendered. Customer support nightmare.",
        "minimal_patch": "try {\n  await grantUserAccess(user_id);\n} catch (err) {\n  alertAdmins('Entitlement failed for paid user', user_id);\n}",
        "verification_steps": ["[ ] Fix the application-specific error preventing the role upgrade."]
    },
    "REFUND_STATE_INCONSISTENCY": {
        "regex_triggers": [
            r"(?i)refund created.*payment_intent\.succeeded.*late.*order marked fulfilled"
        ],
        "severity": "CRITICAL",
        "base_confidence": 98,
        "root_cause": "Refunds override fulfillment. Webhook for `payment_intent.succeeded` arrived late, AFTER the order was refunded manually.",
        "impact": "Giving the product away for free since the refund was already processed.",
        "minimal_patch": "const order = await db.getOrder(orderId);\nif (order.status === 'refunded') {\n  console.warn('Ignoring success webhook for refunded order');\n  return res.status(200).send();\n}",
        "verification_steps": ["[ ] Query the Stripe API or DB to ensure the intent wasn't refunded before fulfilling."]
    },
    
    # ─── Layer 4: Configuration & Edge Cases ───
    "FLOAT_PRECISION_CURRENCY_ERROR": {
        "regex_triggers": [
            r"(?i)currency: eur.*converted: 11\.00",
            r"(?i)float mismatch",
            r"(?i)amount must be at least"
        ],
        "severity": "MEDIUM",
        "base_confidence": 91,
        "root_cause": "Stripe expects minor units (cents). Floating point operations can cause truncation or rounding mismatches.",
        "impact": "Charging wrong amounts or failing Stripe API validation.",
        "minimal_patch": "const amountInCents = Math.round(amountInDollars * 100);",
        "verification_steps": ["[ ] Never use floats for currency math. Use big.js, decimal.js, or integers."]
    },
    "ENVIRONMENT_KEY_MISMATCH": {
        "regex_triggers": [
            r"(?i)sk_test_.*live.*charged in live",
            r"(?i)no such customer.*livemode",
            r"(?i)testmode.*livemode"
        ],
        "severity": "CRITICAL",
        "base_confidence": 96,
        "root_cause": "Cross-contamination of environments. A test key is being used to query a live object, or vice-versa.",
        "impact": "Total API failure. Hard crash.",
        "minimal_patch": "if (process.env.NODE_ENV === 'production') {\n  stripe = new Stripe(process.env.STRIPE_LIVE_SECRET);\n}",
        "verification_steps": ["[ ] Audit your `.env` variables immediately across the pipeline."]
    }
}
