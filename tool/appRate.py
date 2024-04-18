from .dbThrottling import limiter, rate_limit_exceeded_handler,RateLimitExceeded
def appLimitRate(app):
    print('aaa', app, limiter, 222222)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    return app