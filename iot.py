from app import create_app
from app.utils import create_data

app = create_app()

create_data.db_data(app)


if __name__ == '__main__':

    app.run(host='0.0.0.0', port='8081', debug=True, threaded=True, use_reloader=False)



