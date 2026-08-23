#!/usr/bin/env python3
"""Quick test to verify Flask routes are working."""

from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/audit-trail')
def audit_trail():
    return render_template('audit_trail.html')

@app.route('/api-docs')
def api_docs():
    return render_template('api_docs.html')

@app.route('/outputs')
def outputs():
    return render_template('outputs.html')

if __name__ == '__main__':
    print("Testing Flask routes...")
    with app.app_context():
        print("Routes available:")
        for rule in app.url_map.iter_rules():
            if 'settings' in rule.rule or 'audit' in rule.rule or 'api-docs' in rule.rule or 'outputs' in rule.rule:
                print(f"  {rule.rule}")

    print("\nStarting test server on http://localhost:5001")
    app.run(debug=True, port=5001)
