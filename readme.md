Fullstack - Catalog Item Project
=====
###Intro   
This is a project of udacity fullstack nanodegree. Its task is to build a catalog website. It will be able to display different category and items in each category. User will be able to login with google or facebook account. Only logged in user can create, update, delete new category or new item. Unlogged in user can view the category and items not only normaly html page but also json api. This project is deployed on AWS and can be accessed on [catalog website](http://ec2-52-77-221-66.ap-southeast-1.compute.amazonaws.com/)

###Environment   
Before running this web app, first you need to setup environment. Recommend using vagrant. Download the Vagrantfile in the project.   
In the terminal:  

```   
cd path/to/project/dir     
vagrant up       
vagrant ssh      
cd /vagrant    
```


###Requirements   
Then you need to install the several packages, including werkzeug, flask, sqlalchemy, oauth2client, httplib2, requests.    
In the terminal:   

``` 
pip install flask  
pip install SQLAlchemy  
pip install oauth2client  
pip install requests  
pip install httplib2  
pip install werkzeug  

```    

###Run this web app
```
python site.py
```



