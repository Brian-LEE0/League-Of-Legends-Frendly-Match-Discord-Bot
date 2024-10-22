
from app.match_making import app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7070, debug=True)