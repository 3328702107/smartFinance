from . import risk_events, alerts, transactions, users, data_sources, model_stub, auth

def register_blueprints(app):
    app.register_blueprint(risk_events.bp)
    app.register_blueprint(alerts.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(data_sources.bp)
    app.register_blueprint(model_stub.bp)
    app.register_blueprint(auth.bp)