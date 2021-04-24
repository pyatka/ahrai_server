from flask import Flask, render_template
from flask_graphql import GraphQLView

from schema import schema
from middlewares import authorization_middleware

from model import DayModel

app = Flask(__name__)

app.add_url_rule(
    '/',
    view_func=GraphQLView.as_view('graphql',
                                    schema=schema, 
                                    graphiql=False,
                                    middleware=[authorization_middleware]))

@app.route('/render/<day>/<month>/<year>')
def render(day, month, year):
    dm = DayModel(day=int(day), month=int(month), year=int(year))
    ym = dm.get_yesterday()
    return render_template('render.html', today=dm.get_clear_day_data(),
                                          today_str=dm.get_view("%d.%m"),
                                          today_full_str=str(dm),
                                          yesterday_str=ym.get_view("%d.%m"),
                                          today_duty=dm.get_duty_data(), 
                                          yesterday_duty=ym.get_duty_data())

if __name__ == "__main__":
    app.run()