import helpers, dbwrangler, apiapijoyjoy
import unittest
from server import app

class HappyHomeUnitTestCase(unittest.TestCase):
    """unittests for HappyHome"""
    
    def test_validate_address(user_details):
        assert apiapijoyjoy.validate_address

    def test_validate_google_token(token):
        assert apiapijoyjoy.validate_google_token

    # def test_genkey(n):
    #     assert len(apiapijoyjoy.genkey(4)) == 4

    def test_get_current_user():
        assert dbwrangler.get_current_user

    def test_total_houehold_labor(user):
        assert dbwrangler.total_houehold_labor

    def test_individual_labor(user_id):
        assert dbwrangler.individual_labor

    def test_find_days_left(base_chore, userchores, days_left):
        assert helpers.find_days_left

    def test_total_household_labor():
        assert helpers.total_houehold_labor

    def test_color_picker(n_users):
        assert helpers.color_picker

    def test_chores_by_date(user_id):
        assert helpers.chores_by_date

class FlaskTests(TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_some_db_thing(self):
        """Some database test..."""

    def test_newaddress(update_details):
        assert dbwrangler.newaddress

    def test_newchore(name, description, duration_minutes, occurance, by_time, 
                  comment, days_weekly, date_monthly):
        assert dbwrangler.newchore

    def test_add_commitment(days_aggreed, chore_id):
        assert dbwrangler.add_commitment


# def load_tests(loader, tests, ignore):
#     """Also run our doctests and file-based doctests.
#
#     This function name, ``load_tests``, is required.
#     """
#
#     tests.addTests(doctest.DocTestSuite(arithmetic))
#     tests.addTests(doctest.DocFileSuite("tests.txt"))
#     return tests


if __name__ == '__main__':
    # If called like a script, run our tests
    unittest.main()






    @app.route('/')
def index():
    """Homepage."""
    if session.get('user_id', False):
        user = dbwrangler.get_current_user()
        user_id = user.user_id
        #return all chores at this address
        chores = helpers.chores_by_date(user_id)
        now = datetime.utcnow()
        until = now + relativedelta(months=+1)
        month_of_days_dt = rrule(DAILY,dtstart=now,until=until)
        month_of_days = [day.strftime("%A, %B %d, %Y") for day in month_of_days_dt]
        print month_of_days
        pprint.pprint(chores)
        return render_template("dashboard.html", user=user, chores=chores, month=month_of_days)
    else:
        return render_template("homepage.html")


@app.route('/login', methods=['POST'])
def login():
    """Process login"""
    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    flash("Logged in")
    session["user_id"] = user.email  #stores userid pulled from db in session
    return redirect("/")

@app.route("/tokensignin", methods=['POST'])
def validate_via_google():
    token = request.form.get("token")
    print request.form.get
    print apiapijoyjoy.validate_google_token(token)


@app.route('/signup', methods=['GET'])
def signup():
    """Display new user form"""
    return render_template("new_user.html")


@app.route('/signup', methods=['POST'])
def newuser():
    """Process new user"""
    email = request.form.get("email")
    password = request.form.get("password")
    name = request.form.get("name")
    lname = request.form.get("lname")

    new_user = User(email=email, password=password, name=name, lname=lname)

    session["user_id"] = email #Start browser session

    db.session.add(new_user)
    db.session.commit()

    return redirect("/more_info")

@app.route('/gtokensignin', methods=['POST'])
def check_google_token():
    """Take token from login, verify w/Google"""
    gtoken = request.form.get("idtoken")
    g_profile = apiapijoyjoy.validate_google_token(gtoken)
    name = g_profile['given_name']
    lname = g_profile['family_name']
    email = g_profile['email']
    # start a session
    session["user_id"] = email
    user = User.query.filter_by(email=email).first()
    if user:
        return "FLASK SEES USER"
    else:
        new_user = User(email=email, name=name, lname=lname)
        db.session.add(new_user)
        db.session.commit()
        return "FLASK SEES NO USER"

@app.route("/user")
def user_profile():
    """Show user profile"""
    user = dbwrangler.get_current_user()
    address = Address.query.filter_by(address_id=user.address).first()
    return render_template("user.html", user=user, address=address)

@app.route('/more_info')
def new_address():
    """Present new address form"""
    return render_template("new_user_more.html")


@app.route('/complete_registration', methods=['POST'])
def process_address():
    """Add address to user account"""
    user_details = request.form
    update_details = apiapijoyjoy.validate_address(user_details)
    print user_details
    dbwrangler.newaddress(update_details)
    
    return redirect("/")


@app.route('/newchore')
def createchore():
    """Render form to enter new chore for the household"""
    return render_template("newchore.html")


@app.route('/newchore', methods=['POST'])
def newchore():
    """Request form contents to create new chore in db"""
    name = request.form.get('chore_name')
    description = request.form.get('chore_description')
    duration_hours = request.form.get('duration_hours') or 0
    duration_minutes = request.form.get('duration_minutes') or 0
    #compse duration in minutes
    duration_minutes = (int(duration_hours) * 60 + int(duration_minutes))
    occurance = request.form.get('occurance')
    comment = request.form.get('comment')
    by_time = request.form.get('by-time')
    days_weekly = request.form.getlist('days_weekly')
    date_monthly = request.form.get('date_monthly')

    dbwrangler.newchore(name, description, duration_minutes, occurance, by_time, 
                  comment, days_weekly, date_monthly)

    return redirect("/")


@app.route('/takeachore', methods=['GET'])
def claimchore():
    """Display a list of available chores and the days on which they occur, for 
    the user to select and claim"""
    user = dbwrangler.get_current_user()
    userchores = Userchore.query.filter_by(address_id=user.address, 
                                            commitment='INIT').all()
    chores = [Chore.query.filter_by(chore_id=userchore.chore_id).first()
                                     for userchore in userchores]
    for chore in chores:
        chore.days_weekly = chore.days_weekly.split("|")

    return render_template("takeachore.html", chores=chores, 
                            userchores=userchores, user=user)


@app.route('/takechoreform', methods=['POST'])
def feedjsboxes():
    """Get remaining days available for a chore and feed them to JS at takeachore.html"""
    form_chore_id = request.form.get("form_chore_id")
    userchores = Userchore.query.filter_by(chore_id=form_chore_id).all()
    #isolate the item from ^ that is the clean (first) member of that chore inside userchores(table)
    base_userchore = [userchore for userchore in userchores if userchore.commitment == 'INIT']
    #get the rest of the chore data associated with that chore
    base_chore = Chore.query.filter_by(chore_id=base_userchore[0].chore_id).first()
    days_left = base_chore.days_weekly.split("|")
    days_left = helpers.find_days_left(base_chore, userchores, days_left)
    return jsonify({'days_left': days_left,
                    'chore_id': base_chore.chore_id, 
                    'chore_name': base_chore.name,
                    'date_monthly': base_chore.date_monthly,
                    'occurance': base_chore.occurance})


@app.route('/take_weekly_agreements', methods=['POST'])
def take_weekly_agreements():
    """ Get agreed days from form and add them to userchores table in DB, 
        specific to daily and weekly chores"""
    chore_id = request.form.get("chore_id")
    daysagreed = request.form.get("daysagreed")
    daysagreed = daysagreed.split("|")
    days_agreed = [str(i) for i in daysagreed] #No more unicode
    days_agreed = [days_of_the_week[i] for i in range(7) if days_agreed[i] == 'true'] #Cast days from true to dayname
    days_agreed = "|".join(days_agreed)    

    dbwrangler.add_commitment(days_agreed, chore_id)

    return redirect("/takeachore")


@app.route('/take_monthly_agreements', methods=['POST'])
def take_monthly_agreements():

@app.route('/user-contributions.json')
def user_contributions_chart():

@app.route('/logout')
def logout():