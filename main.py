import sqlite3
import sys
from datetime import datetime
from functools import partial
import random
from PyQt5.QtGui import QPainter
from dateutil.relativedelta import relativedelta
from rc_Resources import *  # Import Icons and images from resources file.
from PyQt5.QtCore import Qt, QRectF, QPoint, QTimer
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QMainWindow, QCalendarWidget, QDesktopWidget
from PyQt5.QtChart import QChart, QBarSeries, QBarSet, QBarCategoryAxis, QPieSeries, QPieSlice, QChartView
from PyQt5.uic import loadUi
from ui_MainWindow import *

userId, savingGoal = -1, 0
tableIn_name, tableOut_name = "", ""
Date = datetime.now().date()
Timer = QTimer()
outcome_categories = ["Housing", "Transportation", "Food", "Clothes", "Entertainment", "Bills", "Health", "Other"]
income_categories = ["Salary", "Gift", "Tax repay", "Other"]
Months = {"January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06", "July": "07",
          "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"}
keys = list(Months.keys())
incomeDates = list()
outcomeDates = list()


def gotologin():  # Redirect to login page
    login = LoginScreen()
    widget.addWidget(login)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def gotocreate():  # Redirect to create account page
    create = CreateAccScreen()
    widget.addWidget(create)
    widget.setCurrentIndex(widget.currentIndex() + 1)


class welcomescreen(QDialog):  # load welcome screen
    def __init__(self):
        super(welcomescreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        self.login.clicked.connect(gotologin)
        self.create.clicked.connect(gotocreate)
        self.closebutton.clicked.connect(CloseApp)
        self.Minimize.clicked.connect(MinimizeWindow)


class LoginScreen(QDialog):  # Redirect to login screen
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui", self)  # load login screen
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        self.GoBack.clicked.connect(SwitchUsers)
        self.closebutton.clicked.connect(CloseApp)
        self.Minimize.clicked.connect(MinimizeWindow)

    def loginfunction(self):  # Function to check the validation of the login inputs cross the data with the database.
        user = self.emailfield.text()
        password = self.passwordfield.text()
        if len(user) == 0 or len(password) == 0:  # if field are empty
            self.error.setText("Please enter username and password.")
        else:
            global userId, tableIn_name, tableOut_name, savingGoal
            name = 'SELECT username FROM Users WHERE username =\'' + user + "\'"
            result_name = cur.execute(name).fetchall()
            if not result_name:  # check if user exists.
                self.error.setText("User not exist")
            else:
                query = 'SELECT password FROM Users WHERE username =\'' + user + "\'"
                cur.execute(query)
                result_password = cur.fetchone()[0]
                if result_password == password:  # check if the password is correct.
                    for var in cur.execute('SELECT * FROM Users WHERE username =\'' + user + "\'"):
                        tableIn_name = var[3]
                        tableOut_name = var[4]
                        userId = var[0]
                    savingGoal = cur.execute('SELECT Saving_Goal FROM Budget WHERE Id = ?', (userId,)).fetchone()[0]
                    mainwindow = mainwindowScreen()
                    widget.addWidget(mainwindow)
                    widget.setCurrentIndex(widget.currentIndex() + 1)
                    self.error.setText("")
                else:
                    self.error.setText("Wrong password")


def createAccount(user, password):  # insert user info and init his database.
    global tableIn_name, tableOut_name, userId
    tableIn_name = user + "Income"
    tableOut_name = user + "Outcome"
    user_info = [user, password, tableIn_name, tableOut_name]
    cur.execute('INSERT INTO Users (username, password,tableIn_name ,tableOut_name) VALUES (?,?,?,?)', user_info)
    userId = cur.lastrowid
    cur.execute("""INSERT INTO Budget VALUES(NULL, '0', '0', '0', '0')""")
    cur.execute("""INSERT INTO Users_budget VALUES(?, ?)""", (userId, userId))
    cur.execute("""INSERT INTO Users_Category VALUES(?, ?)""", (userId, userId))
    cur.execute("""INSERT INTO TotalCategory VALUES(NULL, '0', '0', '0', '0', '0', '0', '0', '0')""")
    for i in range(10):
        cur.execute(
            """INSERT INTO IncomePerMonth VALUES('0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', ?, ?)""",
            (2020 + i, userId))
        cur.execute(
            """INSERT INTO OutcomePerMonth VALUES('0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', ?, ?)""",
            (2020 + i, userId))
    cur.execute(  # Create an income table for the new user in the database
        'CREATE TABLE IF NOT EXISTS ' + tableIn_name + ' ("date" TEXT,"price" TEXT,"category" TEXT,"description" TEXT,"BudgetId" INTEGER,"Id" INTEGER,PRIMARY KEY("Id"), FOREIGN KEY("BudgetId") REFERENCES "Budget"("Id"))')
    cur.execute(  # Create an outcome table for the new user in the database
        'CREATE TABLE IF NOT EXISTS ' + tableOut_name + ' ("date" TEXT,"price" TEXT,"category" TEXT,"description" TEXT,"BudgetId" INTEGER,"Id" INTEGER,PRIMARY KEY("Id"), FOREIGN KEY("BudgetId") REFERENCES "Budget"("Id"))')
    conn.commit()


class CreateAccScreen(QDialog):  # load the create account screen
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("createacc.ui", self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.GoBack.clicked.connect(SwitchUsers)
        self.closebutton.clicked.connect(CloseApp)
        self.Minimize.clicked.connect(MinimizeWindow)

    def signupfunction(self):  # Function to check input validations and creates a new account.
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()
        if len(user) == 0 or len(password) == 0 or len(confirmpassword) == 0:  # if fields are empty
            self.error.setText("Please fill in all inputs.")
        elif len(password) < 8 or len(password) > 12:
            self.error.setText("Password have to be 8-12 character long")
        elif password != confirmpassword:
            self.error.setText("Passwords do not match.")
        else:
            createAccount(user, password)
            mainwindow = mainwindowScreen()  # after the account creation loads the main screen.
            widget.addWidget(mainwindow)
            widget.setCurrentIndex(widget.currentIndex() + 1)


def SwitchUsers():  # Function to Reload the welcome screen and switch accounts.
    Welcome = welcomescreen()
    widget.addWidget(Welcome)
    widget.setFixedHeight(600)
    widget.setFixedWidth(800)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def CloseApp():  # Shut down the application.
    conn.close()
    Timer.stop()
    sys.exit()


def MinimizeWindow():  # Minimize the application.
    widget.showMinimized()


def ExplodeSlice(IsBool, Slice):  # Explode the pie slice when the user mouse hoover above it.
    Slice.setExploded(IsBool)
    Slice.setLabelVisible(IsBool)
    if not IsBool:
        Timer.start(750)
    else:
        Timer.stop()


def UpdateMonthlyTotal(month, Year, Type, price):
    cur.execute('SELECT ' + month + ' FROM ' + Type + 'PerMonth WHERE Id=? AND Year=?', (userId, Year))
    monthTotal = float(cur.fetchone()[0])
    monthTotal += price
    cur.execute('UPDATE ' + Type + 'PerMonth SET ' + month + ' = ? WHERE Id=? AND Year=?',
                (str(monthTotal), userId, Year))
    conn.commit()


def displayPieChart(Series):  # Add the series to the chart and return the chart view.
    PieChart = QChart()
    PieChart.addSeries(Series)
    i = 0
    for Slice in Series.slices():
        PieChart.legend().markers(Series)[i].setLabel(Slice.label() + " {:.2f}%".format(100 * Slice.percentage()))
        i += 1
    PieChart.legend().setFont(QtGui.QFont("Monotype Corsiva", 13))
    PieChart.legend().setLabelColor(QtGui.QColor(255, 255, 255))
    PieChart.setBackgroundVisible(False)
    PieChart.setAnimationOptions(QChart.SeriesAnimations)
    PieChart.legend().setVisible(True)
    PieChart.legend().setAlignment(Qt.AlignRight)
    chart_view = QChartView(PieChart)
    chart_view.setRenderHint(QPainter.Antialiasing)
    return chart_view


def addSlice(Series, name, value):  # Add a randomly colored slice to a pie series.
    Slice = Series.append(name, value)
    Slice.setLabelPosition(QPieSlice.LabelInsideHorizontal)
    Slice.setLabelFont(QtGui.QFont("Monotype Corsiva, 16"))
    Slice.setLabelColor(Qt.white)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    Slice.setColor(QtGui.QColor(r, g, b))
    Slice.hovered[bool].connect(partial(ExplodeSlice, Slice=Slice))
    Slice.setExplodeDistanceFactor(0.25)


def initBarGraph(Series):
    Series.setLabelsVisible(True)
    Series.setLabelsAngle(90)
    chart = QChart()
    chart.addSeries(Series)
    chart.setAnimationOptions(QChart.SeriesAnimations)
    AxisX = QBarCategoryAxis()
    AxisX.append(Months)
    AxisX.setLabelsFont(QtGui.QFont("Monotype Corsiva, 16"))
    AxisX.setLabelsColor(Qt.white)
    chart.createDefaultAxes()
    chart.axisY().setLabelsColor(Qt.white)
    chart.axisY().setLabelsFont(QtGui.QFont("Monotype Corsiva, 16"))
    chart.setAxisX(AxisX, Series)
    chart.legend().setVisible(False)
    chart.setBackgroundVisible(False)
    chart_view = QChartView(chart)
    chart_view.setRenderHint(QPainter.Antialiasing)
    return chart_view


def insertDatesToLists():
    for item in cur.execute('SELECT date FROM ' + tableOut_name):
        date = datetime.strptime(item[0], '%d/%m/%Y')
        if date not in outcomeDates:
            outcomeDates.append(date)
    for item in cur.execute('SELECT date FROM ' + tableIn_name):
        date = datetime.strptime(item[0], '%d/%m/%Y')
        if date not in incomeDates:
            incomeDates.append(date)


def slideCategory(button):
    if button.geometry().y() <= -30:
        button.setGeometry(button.geometry().x(), 450, 240, 50)
    else:
        button.setGeometry(button.geometry().x(), button.geometry().y() - 2, 240, 50)


class mainwindowScreen(QMainWindow):  # Main window of the application.
    def __init__(self):
        super(mainwindowScreen, self).__init__()
        loadUi("MainWindow.ui", self)
        self.initMainWindow()
        self.ShowOverview()  # overview page as default home page.
        self.GreetUser()

        def MoveWindow(event):  # Function to drag to app on screen.
            if event.buttons() == Qt.LeftButton:
                widget.move(widget.pos() + event.globalPos() - self.clickPosition)
                self.clickPosition = event.globalPos()
                event.accept()

        self.TopFrame.mouseMoveEvent = MoveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def initTopFrameButtons(self):  # Function to init all the buttons in the top frame.
        self.Overview.clicked.connect(self.ShowOverview)
        self.logo.clicked.connect(self.ShowOverview)
        self.Income.clicked.connect(partial(self.ShowIncomeOutcome, "Income"))
        self.Outcome.clicked.connect(partial(self.ShowIncomeOutcome, "Outcome"))
        self.categories.clicked.connect(self.Showcategories)
        self.closebutton.clicked.connect(CloseApp)
        self.logoutbutton.clicked.connect(SwitchUsers)
        self.Minimize.clicked.connect(MinimizeWindow)

    def initIncomeOutcomeButtons(self):  # Function to init all the buttons in the income/outcome page.
        self.AddIncome.clicked.connect(partial(self.addclicked, "income"))
        self.RemoveIncome.clicked.connect(partial(self.removeclicked, "Income"))
        self.UpdateIncome.clicked.connect(partial(self.updateclicked, "Income"))
        self.AddOutcome.clicked.connect(partial(self.addclicked, "Outcome"))
        self.RemoveOutcome.clicked.connect(partial(self.removeclicked, "Outcome"))
        self.UpdateOutcome.clicked.connect(partial(self.updateclicked, "Outcome"))
        self.IncomeMonths.addItems(Months)
        self.OutcomeMonths.addItems(Months)
        self.IncomeMonths.setCurrentText(datetime.now().strftime('%B'))
        self.OutcomeMonths.setCurrentText(datetime.now().strftime('%B'))
        self.IncomeMonths.currentIndexChanged.connect(partial(self.loadIncomeOutcomedata, "Income"))
        self.OutcomeMonths.currentIndexChanged.connect(partial(self.loadIncomeOutcomedata, "Outcome"))
        self.IncomeMonths.currentIndexChanged.connect(self.updateData)
        self.OutcomeMonths.currentIndexChanged.connect(self.updateData)
        self.IncomeYear.addItems(["2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029"])
        self.IncomeYear.setCurrentText(str(Date.year))
        self.OutcomeYear.addItems(["2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029"])
        self.OutcomeYear.setCurrentText(str(Date.year))
        self.IncomeYear.currentIndexChanged.connect(partial(self.loadIncomeOutcomedata, "Income"))
        self.OutcomeYear.currentIndexChanged.connect(partial(self.loadIncomeOutcomedata, "Outcome"))

    def initCategoriesButtons(self):  # Function to init all the buttons in the categories page.
        self.Housing.clicked.connect(partial(self.SelectedCategory, self.Housing.objectName(), "Outcome"))
        self.Transportation.clicked.connect(partial(self.SelectedCategory, self.Transportation.objectName(), "Outcome"))
        self.Food.clicked.connect(partial(self.SelectedCategory, self.Food.objectName(), "Outcome"))
        self.Clothes.clicked.connect(partial(self.SelectedCategory, self.Clothes.objectName(), "Outcome"))
        self.Entertainment.clicked.connect(partial(self.SelectedCategory, self.Entertainment.objectName(), "Outcome"))
        self.Bills.clicked.connect(partial(self.SelectedCategory, self.Bills.objectName(), "Outcome"))
        self.Health.clicked.connect(partial(self.SelectedCategory, self.Health.objectName(), "Outcome"))
        self.OutcomeOther.clicked.connect(partial(self.SelectedCategory, self.OutcomeOther.objectName(), "Outcome"))
        self.Salary.clicked.connect(partial(self.SelectedCategory, self.Salary.objectName(), "Income"))
        self.Gift.clicked.connect(partial(self.SelectedCategory, self.Gift.objectName(), "Income"))
        self.TaxRepay.clicked.connect(partial(self.SelectedCategory, self.TaxRepay.objectName(), "Income"))
        self.IncomeOther.clicked.connect(partial(self.SelectedCategory, self.IncomeOther.objectName(), "Income"))
        self.CategoryTable.setColumnCount(4)
        self.CategoryTable.setHorizontalHeaderLabels(["Date", "Price", "Category", "Description"])
        self.CategoryTable.setColumnWidth(0, 120)
        self.CategoryTable.setColumnWidth(1, 120)
        self.CategoryTable.setColumnWidth(2, 100)
        self.CategoryTable.setColumnWidth(3, 140)
        self.GoBack.clicked.connect(self.Showcategories)

    def initTable(self):  # Function to init income/outcome table.
        self.Table.setColumnCount(4)
        self.Table.setColumnWidth(0, 120)
        self.Table.setColumnWidth(1, 120)
        self.Table.setColumnWidth(2, 100)
        self.Table.setColumnWidth(3, 140)

    def initMainWindow(self):  # Function to call and init all the features in the application main window.
        self.Year.addItems(["2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029"])
        self.Year.setCurrentText(str(Date.year))
        self.Year.currentIndexChanged.connect(self.BarGraph)
        self.initTopFrameButtons()
        self.initIncomeOutcomeButtons()
        self.initTable()
        self.initCategoriesButtons()
        self.initCalendar()
        self.initProgressIndicator()
        widget.setFixedHeight(700)
        widget.setFixedWidth(1100)
        widget.move(QDesktopWidget().availableGeometry().center().x() - self.frameGeometry().center().x(),
                    QDesktopWidget().availableGeometry().center().y() - self.frameGeometry().center().y())
        Timer.timeout.connect(self.updateRotation)
        self.SliderTimer = QTimer()
        self.SliderTimer.timeout.connect(self.slidingFrame)
        self.SliderTimer.start(50)

    def initProgressIndicator(self):
        self.savingTimer = QTimer()
        self.savingTimer.timeout.connect(self.annotateProgress)
        self.updateGoal.clicked.connect(self.updateSavingGoal)
        if savingGoal == 0:
            self.ProgressTitle.setText("update a saving goal")
            self.DisplaySaving.setVisible(False)
        else:
            self.getBalance()
            self.Goal.setValue(savingGoal)
            self.DisplaySaving.setVisible(True)

    #    """############################################## CALENDER ##################################################"""
    def initCalendar(self):
        self.calendarWidget = CalendarWidget()
        self.calendarWidget.setParent(self.frame_7)
        self.calendarWidget.setGeometry(QtCore.QRect(0, 0, 350, 250))
        self.calendarWidget.setAutoFillBackground(False)
        self.calendarWidget.setStyleSheet("background-color: transparent;\n"
                                          "alternate-background-color: transparent;\n"
                                          "selection-background-color: rgb(255, 170, 0);")
        self.calendarWidget.setMinimumDate(QtCore.QDate(2020, 1, 1))
        self.calendarWidget.setMaximumDate(QtCore.QDate(2029, 12, 31))
        self.calendarWidget.setGridVisible(False)
        self.calendarWidget.setSelectionMode(QtWidgets.QCalendarWidget.SingleSelection)
        self.calendarWidget.setHorizontalHeaderFormat(QtWidgets.QCalendarWidget.ShortDayNames)
        self.calendarWidget.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.calendarWidget.setDateEditEnabled(True)
        self.calendarWidget.setObjectName("calendarWidget")
        self.calendarWidget.clicked.connect(self.DateData)
        self.calendarWidget.setFont(QtGui.QFont("Monotype Corsiva", 12))

    def DateData(self, qDate):  # Function that gets the selected date and display the income/outcome data on the lists
        self.IncomeList.clear()  # clears the lists from old data.
        self.OutcomeList.clear()
        if qDate.day() > 9:  # fix the date format
            if qDate.month() > 9:
                date = '{0}/{1}/{2}'.format(qDate.day(), qDate.month(), qDate.year())
            else:
                date = '{0}/0{1}/{2}'.format(qDate.day(), qDate.month(), qDate.year())
        else:
            if qDate.month() > 9:
                date = '0{0}/{1}/{2}'.format(qDate.day(), qDate.month(), qDate.year())
            else:
                date = '0{0}/0{1}/{2}'.format(qDate.day(), qDate.month(), qDate.year())
        for var in cur.execute('SELECT * FROM ' + tableIn_name + ' WHERE date =?',
                               (date,)):  # Display the data on the Income list.
            data = var[3] + " :"
            self.IncomeList.addItem(data)
            price = "+" + var[1]
            self.IncomeList.addItem(price)
        for var in cur.execute('SELECT * FROM ' + tableOut_name + ' WHERE date =?',
                               (date,)):  # Display the data on the Outcome list.
            data = var[3] + " :"
            self.OutcomeList.addItem(data)
            price = "-" + var[1]
            self.OutcomeList.addItem(price)

    def GreetUser(self):  # Function that greet the user according to the time of the day
        cur.execute('SELECT username FROM Users WHERE Id =?', (userId,))
        CurrentName = cur.fetchone()[0]
        self.User_Name.setText(CurrentName)  # Display user name in the app
        hour = datetime.now().hour
        if 6 < hour < 18:  # if day time
            self.Sun.setVisible(True)
            self.Moon.setVisible(False)
            if 6 < hour < 12:
                self.Greeting.setText("Good Morning,")
            else:
                self.Greeting.setText("Good Day,")
        else:  # night time
            self.Sun.setVisible(False)
            self.Moon.setVisible(True)
            if 18 < hour < 23:
                self.Greeting.setText("Good Evening,")
            else:
                self.Greeting.setText("Good Night,")

#   ######################################     Category Slider     ##########################################
    def slidingFrame(self):  # Sliding categories.
        slideCategory(self.HousingSlider)
        slideCategory(self.TransportationSlider)
        slideCategory(self.FoodSlider)
        slideCategory(self.ClothesSlider)
        slideCategory(self.EntertainmentSlider)
        slideCategory(self.BillsSlider)
        slideCategory(self.HealthSlider)
        slideCategory(self.OtherSlider)

    def loadDataToSlider(self):     # Loads the data into the slider objects
        for var in cur.execute('SELECT * FROM TotalCategory WHERE Id=? ', (userId,)):
            self.HousingSlider.setText("Housing - " + var[1] + " ₪")
            self.TransportationSlider.setText("Transportation - " + var[2] + " ₪")
            self.FoodSlider.setText("FoodSlider - " + var[3] + " ₪")
            self.ClothesSlider.setText("Clothes - " + var[4] + " ₪")
            self.EntertainmentSlider.setText("Entertainment - " + var[5] + " ₪")
            self.BillsSlider.setText("Bills - " + var[6] + " ₪")
            self.HealthSlider.setText("Health - " + var[7] + " ₪")
            self.OtherSlider.setText("Other - " + var[8] + " ₪")

#    """############################################## Progress Indicator ##################################################"""
    def progressBarValue(self, value):      # Function to display the saving monthly progress.
        styleSheet = """QFrame{
        border-radius: 100px;
        background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} rgba(85, 170, 255, 255));
        }"""
        htmlText = """< html > < head / > < body > < p > < span
        style = " vertical-align:super;" >{VALUE}/ < / span > < span
        style = " vertical-align:sub;" >{SavingValue}< / span > < / p > < / body > < / html >"""
        self.DisplaySaving.setText(htmlText.replace("{VALUE}", str(value)).replace("{SavingValue}", str(savingGoal)))
        value = value / savingGoal
        if value >= 1.000:
            stop_1 = "1.000"
            stop_2 = "1.000"
        elif value <= 0:
            stop_1 = "0.999"
            stop_2 = "1.000"
        else:
            progress = (1 - value)
            stop_1 = str(progress - 0.001)
            stop_2 = str(progress)
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)
        self.CircularFrame.setStyleSheet(newStylesheet)

    def updateSavingGoal(self):     # Function to update the user saving goal.
        global savingGoal
        savingGoal = self.Goal.value()
        cur.execute("UPDATE Budget SET Saving_Goal =? WHERE Id =?", (savingGoal, userId))
        conn.commit()
        self.DisplaySaving.setVisible(True)
        self.getBalance()

    def getBalance(self):       # function to retrieve the monthly balance.
        self.Title.setText("Saving goal for " + self.OutcomeMonths.currentText())
        self.monthlyBalance = 0
        outcome = cur.execute("SELECT " + self.OutcomeMonths.currentText() + " FROM OutcomePerMonth WHERE Id=? AND year=?", (userId, self.OutcomeYear.currentText())).fetchone()[0]
        income = cur.execute("SELECT " + self.OutcomeMonths.currentText() + " FROM IncomePerMonth WHERE Id=? AND year=?", (userId, self.OutcomeYear.currentText())).fetchone()[0]
        self.monthlyBalance = float(income) - float(outcome)
        self.setBalanceTitle(self.monthlyBalance)
        self.progressBarValue(self.monthlyBalance)
        self.counter = 0
        self.savingTimer.start(100)

    def setBalanceTitle(self, balance):     # Function that set the progress title according to the data
        if balance < savingGoal / 4:
            self.ProgressTitle.setText("Bad work this month")
        elif balance < savingGoal / 2:
            self.ProgressTitle.setText("Need to do better")
        elif balance < savingGoal:
            self.ProgressTitle.setText("Almost there")
        else:
            self.ProgressTitle.setText("Excellent work this month!")

    def annotateProgress(self):     # Function to annotate the progress indicator.
        if self.counter > self.monthlyBalance:
            self.counter = self.monthlyBalance
            self.progressBarValue(self.counter)
        elif self.counter == self.monthlyBalance:
            self.counter = 0
            self.savingTimer.stop()
        else:
            self.progressBarValue(self.counter)
            self.counter += int(self.monthlyBalance/10)

    #    """############################################## INCOME/OUTCOME ##################################################"""
    def ShowIncomeOutcome(self, Type):  # Load income/outcome page.
        self.stackedWidget.setCurrentWidget(self.incomeoutcomepage)
        if Type == 'Outcome':  # display the relevant buttons for outcome
            self.OutcomeMonths.setCurrentText(self.IncomeMonths.currentText())
            self.OutcomeYear.setCurrentText(self.IncomeYear.currentText())
            self.IsOutcome(True)
        else:  # display the relevant buttons for income
            self.IncomeMonths.setCurrentText(self.OutcomeMonths.currentText())
            self.IncomeYear.setCurrentText(self.OutcomeYear.currentText())
            self.IsOutcome(False)
        self.total.setText("Total " + Type + ":")
        self.headTitle.setText(Type)
        self.loadIncomeOutcomedata(Type)

    def IsOutcome(self, Bool):  # show relevant buttons for income/outcome.
        self.IncomeMonths.setVisible(not Bool)
        self.OutcomeMonths.setVisible(Bool)
        self.AddIncome.setVisible(not Bool)
        self.AddOutcome.setVisible(Bool)
        self.RemoveIncome.setVisible(not Bool)
        self.RemoveOutcome.setVisible(Bool)
        self.UpdateIncome.setVisible(not Bool)
        self.UpdateOutcome.setVisible(Bool)
        self.IncomeYear.setVisible(not Bool)
        self.OutcomeYear.setVisible(Bool)

    def removeclicked(self, Type):  # Function to remove a selected row from the database.
        index = self.Table.currentRow()
        date = self.Table.item(index, 0).text()
        description = self.Table.item(index, 3).text()
        price = -float(self.Table.item(index, 1).text())
        newDate = datetime.strptime(date, '%d/%m/%Y')
        if Type == "Outcome":
            cur.execute('DELETE FROM ' + tableOut_name + ' WHERE date =? AND description=?', (date, description,))
        else:
            cur.execute('DELETE FROM ' + tableIn_name + ' WHERE date =? AND description=?', (date, description,))
        conn.commit()
        UpdateMonthlyTotal(keys[newDate.month - 1], newDate.year, Type, price)
        self.loadIncomeOutcomedata(Type)

    def addclicked(self, Type):  # load the add income window.
        Add = addwindow(Type)
        Add.setModal(True)
        Add.exec_()
        self.loadIncomeOutcomedata(Type)

    def updateclicked(self, Type):  # load the update income window and check if the row is updatable.
        index = self.Table.currentRow()
        if index == -1:
            self.ErrorMessage.setText("Choose a row you \nwant to update")
        else:
            self.ErrorMessage.setText("")
            date = self.Table.item(index, 0).text()
            description = self.Table.item(index, 3).text()
            if Type == 'Outcome':
                cur.execute('SELECT * FROM ' + tableOut_name + ' WHERE date =? AND description=?', (date, description,))
            else:
                cur.execute('SELECT * FROM ' + tableIn_name + ' WHERE date =? AND description=?', (date, description,))
            data = cur.fetchall()
            conn.commit()
            self.ErrorMessage.setText("")
            update = updatewindow(data, Type)
            update.setModal(True)
            update.exec_()
            self.loadIncomeOutcomedata(Type)

    def loadIncomeOutcomedata(self, Type):  # Function to load and display the Income/Outcome data on a table.
        while self.Table.rowCount() > 0:
            self.Table.removeRow(0)
        self.Table.setHorizontalHeaderLabels(["Date", "Price", "Category", "Description"])
        if Type == 'Outcome':
            results = cur.execute('SELECT * FROM ' + tableOut_name)
            month = self.OutcomeMonths.currentText()
            year = self.OutcomeYear.currentText()
        else:
            results = cur.execute('SELECT * FROM ' + tableIn_name)
            month = self.IncomeMonths.currentText()
            year = self.IncomeYear.currentText()
        TableRow = 0
        Total = 0.
        for row in results:
            date = row[0].split('/')
            if date[1] == Months[month] and date[2] == year:
                self.Table.setRowCount(TableRow + 1)  # Increase Table row count
                self.Table.setItem(TableRow, 0, QtWidgets.QTableWidgetItem(row[0]))
                self.Table.setItem(TableRow, 1, QtWidgets.QTableWidgetItem(row[1]))
                self.Table.setItem(TableRow, 2, QtWidgets.QTableWidgetItem(row[2]))
                self.Table.setItem(TableRow, 3, QtWidgets.QTableWidgetItem(row[3]))
                TableRow += 1
                Total += float(row[1])
        self.Balance.display(Total)  # Display monthly total income/outcome
        if Type == 'Outcome':
            cur.execute('UPDATE Budget SET Total_Outcome = ? WHERE Id = ?', (Total, userId))
        else:
            cur.execute('UPDATE Budget SET Total_Income = ? WHERE Id = ?', (Total, userId))
        conn.commit()

    #    """############################################## OVERVIEW ##################################################"""
    def ShowOverview(self):  # Load the overview page.
        self.stackedWidget.setCurrentWidget(self.overviewpage)
        self.BarGraph()  # Load the Bar chart in the overview page.
        self.PieGraph()  # Load the Pie chart in the overview page.
        self.getBalance()
        insertDatesToLists()

    def BarGraph(self):  # function to load and display data on a bar graph.
        IncomeSet = QBarSet("Income")
        for var in cur.execute('SELECT * FROM IncomePerMonth WHERE Id=? AND Year=?', (userId, self.Year.currentText())):
            IncomeSet.append([float(var[0]), float(var[1]), float(var[2]), float(var[3]), float(var[4]), float(var[5]),
                              float(var[6]), float(var[7]), float(var[8]), float(var[9]), float(var[10]),
                              float(var[11])])
        IncomeSet.setLabelFont(QtGui.QFont("Monotype Corsiva", 12))
        OutcomeSet = QBarSet("Outcome")
        for var in cur.execute('SELECT * FROM OutcomePerMonth WHERE Id=? AND Year=?',
                               (userId, self.Year.currentText())):
            OutcomeSet.append([float(var[0]), float(var[1]), float(var[2]), float(var[3]), float(var[4]), float(var[5]),
                               float(var[6]), float(var[7]), float(var[8]), float(var[9]), float(var[10]),
                               float(var[11])])
        OutcomeSet.setLabelFont(QtGui.QFont("Monotype Corsiva", 12))
        IncomeSet.setColor(Qt.darkGreen)
        OutcomeSet.setColor(Qt.red)
        Series = QBarSeries()
        Series.append(IncomeSet)
        Series.append(OutcomeSet)
        while self.BarFrame.count() > 0:  # Remove the former graph
            item = self.BarFrame.takeAt(0)
            self.BarFrame.removeWidget(item.widget())
        self.BarFrame.addWidget(initBarGraph(Series))  # Display the chart

    def PieGraph(self):  # function to load and display data on a pie graph.
        self.Series = QPieSeries()
        self.updateData()
        TotalOut = []
        for var in cur.execute('SELECT * FROM TotalCategory WHERE id=?',
                               (userId,)):  # Gets the total for each category from the database
            TotalOut = [var[1], var[2], var[3], var[4], var[5], var[6], var[7], var[8]]
        length = len(outcome_categories)
        for i in range(length):  # Append data into slices.
            addSlice(self.Series, outcome_categories[i], float(TotalOut[i]))
        Timer.start(750)
        while self.PieFrame.count() > 0:  # Clear former chart.
            item = self.PieFrame.takeAt(0)
            self.PieFrame.removeWidget(item.widget())
        self.PieFrame.addWidget(displayPieChart(self.Series))  # Display the chart
        item = self.PieFrame.itemAt(0)
        item.widget().setFixedSize(500, 420)

    def updateRotation(self):  # Init rotation for the pie chart.
        shift = random.randrange(0, 120)
        self.Series.setPieStartAngle(self.Series.pieStartAngle() + shift)
        self.Series.setPieEndAngle(self.Series.pieEndAngle() + shift)

    def updateData(self):  # update the pie chart data for the chosen month.
        self.PieTitle.setText("Total expenses by categories for " + self.OutcomeMonths.currentText())
        categories = {"Housing": 0, "Transportation": 0, "Food": 0, "Clothes": 0, "Entertainment": 0, "Bills": 0,
                      "Health": 0, "Other": 0}
        for item in cur.execute('SELECT * FROM ' + tableOut_name):
            date = item[0].split('/')
            if date[1] == Months[self.OutcomeMonths.currentText()] and date[2] == self.OutcomeYear.currentText():
                categories[item[2]] += float(item[1])
        for category in categories:
            cur.execute('UPDATE TotalCategory SET ' + category + ' =? WHERE Id = ?',
                        (str(categories[category]), userId))
        conn.commit()
        self.loadDataToSlider()

    #    """############################################## CATEGORIES ##################################################"""
    def Showcategories(self):  # Load categories page and init all buttons.
        self.stackedWidget.setCurrentWidget(self.categoriespage)
        self.stackedCategory.setCurrentWidget(self.CategoriesPage)

    def SelectedCategory(self, name, Type):  # Function that load and display the category data on a table and a graph.
        if name == 'IncomeOther' or name == 'OutcomeOther':  # change the names to match the name inside the database.
            name = 'Other'
        elif name == 'TaxRepay':
            name = 'Tax Repay'
        self.stackedCategory.setCurrentWidget(self.CategoryData)  # load the category display page.
        self.Name.setText(name)
        self.MonthLabel.setText(self.OutcomeMonths.currentText())
        Total = self.loadCategoryTable(Type, name)
        Series = QPieSeries()
        addSlice(Series, name, Total)
        if Type == 'Outcome':  # Display total income/outcome for the chosen category and exec SQL query
            self.TotalCate.setText("Total spent on " + name + " this month: " + str(Total) + " ₪")
            cur.execute('SELECT Total_Outcome FROM Budget WHERE id =?', (userId,))
            total = float(cur.fetchone()[0])
            self.TotalSpent.setText("Total spent this month:" + str(total) + " ₪")
        else:
            self.TotalCate.setText("Total income for " + name + " : " + str(Total) + " ₪")
            cur.execute('SELECT Total_Income FROM Budget WHERE id =?', (userId,))
            total = float(cur.fetchone()[0])
            self.TotalSpent.setText("Total income this month:" + str(total) + " ₪")
        total -= Total
        addSlice(Series, "Total", total)
        Series.setHoleSize(0.35)
        while self.CategoryPieFrame.count() > 0:  # clears old data.
            item = self.CategoryPieFrame.itemAt(0)
            self.CategoryPieFrame.removeWidget(item.widget())
        self.CategoryPieFrame.addWidget(displayPieChart(Series))  # Add the donut chart to the frame.
        item = self.CategoryPieFrame.itemAt(0)
        item.widget().setFixedSize(420, 330)
        conn.commit()

    def loadCategoryTable(self, Type, name):
        while self.CategoryTable.rowCount() > 0:  # Clear old data.
            self.CategoryTable.removeRow(0)
        if Type == 'Outcome':  # Set table header and run SQL query for outcome / income.
            results = cur.execute('SELECT * FROM ' + tableOut_name + ' WHERE Category=?', (name,))
            month = self.OutcomeMonths.currentText()
            year = self.OutcomeYear.currentText()
        else:
            results = cur.execute('SELECT * FROM ' + tableIn_name + ' WHERE Category=?', (name,))
            month = self.IncomeMonths.currentText()
            year = self.IncomeYear.currentText()
        TableRow = 0
        Total = 0.00
        for row in results:
            date = row[0].split('/')
            if date[1] == Months[month] and date[2] == year:
                self.CategoryTable.setRowCount(TableRow + 1)  # Increase table row count.
                self.CategoryTable.setItem(TableRow, 0, QtWidgets.QTableWidgetItem(row[0]))
                self.CategoryTable.setItem(TableRow, 1, QtWidgets.QTableWidgetItem(row[1]))
                self.CategoryTable.setItem(TableRow, 2, QtWidgets.QTableWidgetItem(row[2]))
                self.CategoryTable.setItem(TableRow, 3, QtWidgets.QTableWidgetItem(row[3]))
                TableRow += 1
                Total += float(row[1])
        return Total


# #########################################   Calendar class  #########################################
class CalendarWidget(QCalendarWidget):  # class to modify the application calendar widget.
    def paintCell(self, painter, rect, date):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.save()
        if not date.month() == self.monthShown():  # if date not in the current month.
            painter.setPen(Qt.black)
        elif date.dayOfWeek() == 6:  # if Saturday.
            painter.setPen(Qt.red)
        else:
            painter.setPen(Qt.white)
        painter.drawRect(rect)
        if date in outcomeDates:  # Add a small red ellipse to indicate an outcome.
            painter.setBrush(Qt.red)
            painter.drawEllipse(rect.bottomLeft() + QPoint(20, -3), 4, 4)
        if date in incomeDates:  # Add a small green ellipse to indicate an income.
            painter.setBrush(Qt.green)
            painter.drawEllipse(rect.bottomLeft() + QPoint(30, -3), 4, 4)
        painter.drawText(QRectF(rect), Qt.TextSingleLine | Qt.AlignCenter, str(date.day()))
        painter.restore()


# #########################################  Add Window   #########################################
def addStandingOrder(price, category, description, newDate,
                     Type):  # Add the same outcome/income for the next 12 months as a standing order.
    for i in range(12):
        future_date = newDate + relativedelta(months=i)
        if Type == 'Outcome':
            cur.execute(
                'INSERT INTO ' + tableOut_name + ' (date, price, category, description, BudgetId) VALUES (?,?,?,?,?)',
                (future_date.strftime('%d/%m/%Y'), price, category, description, userId))
        else:
            cur.execute(
                'INSERT INTO ' + tableIn_name + ' (date, price, category, description, BudgetId) VALUES (?,?,?,?,?)',
                (future_date.strftime('%d/%m/%Y'), price, category, description, userId))
        UpdateMonthlyTotal(keys[future_date.month - 1], future_date.year, Type, float(price))


class addwindow(QDialog):  # Loads the add outcome window
    def __init__(self, Type):
        super(addwindow, self).__init__()
        loadUi("addwindow.ui", self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.DateInput.setDate(Date)
        self.NumPayments.setVisible(False)
        Num = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.NumPayments.addItems(Num)
        if Type == "Outcome":
            self.CategoryInput.addItems(outcome_categories)
            self.Payments.setVisible(True)
        else:
            self.CategoryInput.addItems(income_categories)
            self.Payments.setVisible(False)
        self.Payments.toggled.connect(self.paymentsToggled)
        self.AddButton.clicked.connect(partial(self.addedclicked, Type))
        self.CancelButton.clicked.connect(self.close)
        self.closebutton.clicked.connect(self.close)

    def paymentsToggled(self):
        if self.Payments.isChecked():
            self.NumPayments.setVisible(True)
        else:
            self.NumPayments.setVisible(False)

    def addedclicked(self, Type):  # Function that receive and enter the user inputs into the database.
        if self.Payments.isChecked() and self.StandingOrder.isChecked():
            self.Error.setText("Can't mark payments and standing order together.")
        else:
            self.Error.setText("")
            price = self.PriceInput.text()
            category = self.CategoryInput.currentText()
            date = self.DateInput.text()
            description = self.DescriptionInput.text()
            TotalCategory = 0.00
            newDate = datetime.strptime(date, '%d/%m/%Y')
            if Type == "Outcome":
                if self.Payments.isChecked():  # If user selected payments.
                    self.addPayments(price, category, description, newDate, Type)
                elif self.StandingOrder.isChecked():
                    addStandingOrder(price, category, description, newDate, Type)
                else:
                    cur.execute(
                        'INSERT INTO ' + tableOut_name + ' (date, price, category, description, BudgetId) VALUES (?,?,?,?,?)',
                        (date, price, category, description, userId))
                    UpdateMonthlyTotal(keys[newDate.month - 1], newDate.year, Type, float(price))
                for var in cur.execute('SELECT price FROM ' + tableOut_name + '  WHERE category=?', (category,)):
                    TotalCategory += float(var[0])  # updates the total outcome for the selected category.
                cur.execute('UPDATE TotalCategory SET ' + category + ' = ? WHERE Id = ?', (TotalCategory, userId))
            else:
                if self.StandingOrder.isChecked():
                    addStandingOrder(price, category, description, newDate, Type)
                else:
                    cur.execute(
                        'INSERT INTO ' + tableIn_name + ' (date, price, category, description, BudgetId) VALUES (?,?,?,?,?)',
                        (date, price, category, description, userId))
                    UpdateMonthlyTotal(keys[newDate.month - 1], newDate.year, Type, float(price))
            conn.commit()
            self.close()  # close window.

    def addPayments(self, price, category, description, newDate, Type):  # adding payments into the database.
        payments = int(self.NumPayments.currentText())
        pay = float(price) / payments  # Divide the price for the amount of payments
        for i in range(payments):
            future_date = newDate + relativedelta(months=i)  # Add a payment for the coming months.
            PaymentDescription = description + ' (payments)(' + str(
                payments - i) + ')'  # Describe how many payments are left.
            cur.execute(
                'INSERT INTO ' + tableOut_name + ' (date, price, category, description, BudgetId) VALUES (?,?,?,?,?)',
                (future_date.strftime('%d/%m/%Y'), pay, category, PaymentDescription, userId))
            UpdateMonthlyTotal(keys[future_date.month - 1], future_date.year, Type, pay)


class updatewindow(QDialog):  # Loads the update outcome window and selected item data.
    def __init__(self, data, Type):
        super(updatewindow, self).__init__()
        loadUi("updatewindow.ui", self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        for var in data:
            if Type == "Outcome":
                self.CategoryInput.addItems(outcome_categories)
            else:
                self.CategoryInput.addItems(income_categories)
            self.DateInput.setDate(datetime.strptime(var[0], '%d/%m/%Y').date())
            self.PriceInput.setValue(float(var[1]))
            self.CategoryInput.setCurrentText(var[2])
            self.DescriptionInput.setText(var[3])
        self.UpdateButton.clicked.connect(partial(self.updateclicked, Type, data))
        self.CancelButton.clicked.connect(self.close)
        self.closebutton.clicked.connect(self.close)

    def updateclicked(self, Type,
                      data):  # Function that receives the user input and update the selected row in the database.
        price = self.PriceInput.text()
        category = self.CategoryInput.currentText()
        date = self.DateInput.text()
        description = self.DescriptionInput.text()
        newDate = datetime.strptime(date, '%d/%m/%Y')
        for item in data:
            NewPrice = float(price) - float(item[1])
            if Type == "Outcome":  # Enter data to outcome table and update the total Category sum.
                cur.execute(
                    'UPDATE ' + tableOut_name + ' SET  date =?, price =?, category =?, description =?  WHERE date =? AND description=?',
                    (date, price, category, description, item[0], item[3]))
                TotalCategory = 0.00
                for var in cur.execute('SELECT * FROM ' + tableOut_name + '  WHERE category=?', (category,)):
                    splitDate = var[0].split('/')
                    if int(splitDate[1]) == newDate.month and int(splitDate[2]) == newDate.year:
                        TotalCategory += float(var[1])
                cur.execute('UPDATE TotalCategory SET ' + category + ' = ? WHERE Id = ?', (TotalCategory, userId))
                UpdateMonthlyTotal(keys[newDate.month - 1], newDate.year, Type, NewPrice)
            else:  # Enter data to income table.
                cur.execute(
                    'UPDATE ' + tableIn_name + ' SET date =?, price =?, category =?, description =? WHERE date =? AND description=?',
                    (date, price, category, description, item[0], item[3]))
                UpdateMonthlyTotal(keys[newDate.month - 1], newDate.year, Type, NewPrice)
        conn.commit()
        self.close()


def initDataBase():  # Function to create all the database in the first use.
    cur.execute(
        'CREATE TABLE IF NOT EXISTS Users ("Id" INTEGER, "username" TEXT, "password" TEXT, "tableIn_name" TEXT, "tableOut_name" TEXT, PRIMARY KEY("Id"))')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS TotalCategory ("Id"	INTEGER, "Housing" TEXT, "Transportation" TEXT, "Food" TEXT, "Clothes" TEXT, "Entertainment" TEXT, "Bills" TEXT, "Health" TEXT, "Other" TEXT, PRIMARY KEY("Id"))')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS Users_Category ("UserId" INTEGER, "CategoryId"	INTEGER, FOREIGN KEY("CategoryId") REFERENCES "TotalCategory"("Id"), FOREIGN KEY("UserId") REFERENCES "Users"("Id"))')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS Budget ("Id" INTEGER, "Total_Outcome" TEXT, "Total_Income" TEXT, "Balance" TEXT, "Saving_Goal" INTEGER, PRIMARY KEY("Id"))')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS Users_budget ("UserId" INTEGER, "BudgetId" INTEGER, FOREIGN KEY("BudgetId") REFERENCES "Budget"("Id"), FOREIGN KEY("UserId") REFERENCES "Users"("Id"))')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS IncomePerMonth ("January" TEXT,"February" TEXT, "March"	TEXT, "April" TEXT, "May" TEXT, "June" TEXT, "July" TEXT, "August" TEXT, "September" TEXT, "October" TEXT, "November" TEXT, "December" TEXT, "Year"	INTEGER, "Id" INTEGER, FOREIGN KEY("Id") REFERENCES "Users"("Id"))')
    conn.commit()


# main
app = QApplication(sys.argv)
app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
conn = sqlite3.connect("Budget_data.db")
cur = conn.cursor()
initDataBase()
welcome = welcomescreen()
widget = QStackedWidget()
widget.addWidget(welcome)
widget.setWindowFlag(Qt.FramelessWindowHint)
widget.setFixedHeight(600)
widget.setFixedWidth(800)
widget.show()
sys.exit(app.exec_())
