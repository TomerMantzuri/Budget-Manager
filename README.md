# Budget-Manager

A Python desktop application using PyQt5, the application UI designed by QT Designer.

This application can support many users, for each user the app create his own database for income/outcome.

Each user have to sign up first, once the user insert data as outcome or income, the app will display the data summary on different charts, calender, progress indicator and more.

The available dates on the app are from 1/1/2020 until 31/12/2029.

A few screenshots from the application :

welcome page:

![](screenshots/login%20page.jpg)

overview page:  

![](screenshots/main%20window.jpg)


outcome page:

![](screenshots/outcome%20nov.jpg)

categories page:  

![](screenshots/categories%20page.jpg)

over view page of a diffrent month while mouse hoovering the pie chart:  

![](screenshots/Explode%20Slice.jpg)


* The category list on the button right is running on a diffrent thread sliding the categories with thier total spending for the selected month,
so as the pie chart which is spinning unless the mouse hoovers a slice.
* According to the monthly balance and the user monthly saving goal, the application display a motivation sentences.
