# aspen

**aspen** is a personal web content management system based 
[webpy](http://webpy.org), see example: [http://lw1990.name](http://lw1990.name)

## Why name *aspen*
Aspen is a kind of pulpwood commonly used for paper making. Literally, *aspen* 
is a pen, symbolically *aspen* is paper. With *aspen*, I will publish ideas and 
views through *aspen*.

## Author
[Â¬Íþ (LU WEI)](http://lw1990.name)

## Features
*aspen* contains two major parts. One is for reader, aspen.py. The  other is for
the system owner, admin.py. 

For owner:

- change your personal information
- administrate posts: new, edit, delete
- upload static files

For reader:

- view post entries list: whole publised list, by tag, by category 
- view post

## Dependency
First, you need python be installed(2.7.x)

- [webpy](http://webpy.org)
- [hoedown](https://github.com/hhatto/python-hoedown)
- [pygments](http://pygments.org)

## Install
*   Just Try:

    Go to the dirtory of aspen, run `python aspen.py`, then visit 
http://0.0.0.0:8080 

*   Deploy(Apache with mod_wsgi on Ubuntu)

1.  Change /etc/apache2/sites-available/default.conf (or as you like another 
site configure)

    ```
        <VirtualHost _default_ *:80> 
        ServerAdmin admin@project.com 
        DocumentRoot /var/www/aspen/static/ 
        ErrorLog /var/www/aspen/logs/error.log 
        CustomLog /var/www/aspen/logs/access.log combined  
        WSGIScriptAlias / /var/www/aspen/aspen.py 
        Alias /static /var/www/aspen/static 
        AddType text/html .py 
        WSGIDaemonProcess www-data threads=15 
        WSGIProcessGroup www-data  
        <Directory /var/www/aspen/> 
        Order deny,allow 
        Allow from all Options +FollowSymLinks 
        Options -Indexes 
        </Directory>  
        </VirtualHost>
    ```
2.  Change owner of files requiring write access to apache¡¯s www-data

  `sudo chown -R www-data *files or Dir requiring write access*`
3.  Try to run, restart apache2, and see http://example.com

  `sudoservice apache2 restart`
4.  administrate
You can administrate your site at http://example.com/admin/, the initial user
name is *admin*, and password is *admin*

## License
See [MIT License](http://mit-license.org/)
## Contact
whuluwei\[@\]gmail\[dot\]com
