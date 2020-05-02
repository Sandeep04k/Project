from flask import Flask, render_template, request, escape, session
from vowels import searchforletters

from threading import Thread

from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError
from dec import check_logged_in

app = Flask(__name__)


app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'sandeep',
                          'password': 'password',
                          'database': 'search4webDB', }

@app.route('/login')
def do_login():
    session['logged_in']=True
    return 'you are now logged in '

@app.route('/logout')
def do_logout() ->str:
    session.pop('logged_in')
    return 'you are not logged in'


def log_request(req: 'flask request', res: str) ->None:
    """log details of web requests"""

    with UseDatabase(app.config['dbconfig']) as cursor:

        _sql = """insert into log 
                  (word, letters, ip, browser_string, results)
                   values  
                  ( %s, %s, %s, %s, %s)"""
        cursor.execute(_sql, (req.form['word'],
                              req.form['letters'],
                              req.remote_addr,
                              req.user_agent.browser,
                              res ))



@app.route('/search4', methods=['POST','GET'])
def do_search() -> 'html':

    word = request.form['word']
    letters = request.form['letters']
    title = 'The result is:'
    results = str(searchforletters(word, letters))
    log_request(request,results)
    return render_template('results.html', the_word=word, the_title=title, the_letters=letters, the_results=results,)


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html', the_title='Welcome to searchforletters on the web')


@app.route('/viewlog')
@check_logged_in

def view_the_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
             _SQL = """select word, letters, ip, browser_string, results from log"""
             cursor.execute(_SQL)
             contents = cursor.fetchall()

        titles = ('Word','Letters', 'Remote_addr', 'User_agent', 'Results')
        return render_template('viewlog.html', the_title='View log', the_row_titles=titles, the_data=contents,)

    except ConnectionError as err:
        print('Is your database switched on', str(err))

    except CredentialsError as err:
        print('User-id/Password issues', str(err))

    except SQLError as err:
        print('is your query correct', str(err))

    except Exception as err:
        print('something went wrong',str(err))
    return 'Error'

app.secret_key = 'youwillneverguessit'

if __name__ == '__main__':
    app.run(debug=True)


