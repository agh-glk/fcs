
******************
Quickstart
******************

Short instruction presenting how to launch Focused Crawling Search.

.. note:: Unix-based operation system and Vagrant(preferred 1.35 or higher) are required.

#. Download project code from Github `repository <https://github.com/agh-glk/fcs>`_.
#. Change directory into :file:`/fcs`.
#. In command line type ``vagrant up``. Virtual machine with all requirements will be provisioned. Its ip address is ``192.168.0.2``.
#. Start second shell, in both of them:

    * connect to machine with ``vagrant ssh``,
    * activate python virtual environment: ``source ./fcs/bin/activate``,
    * move to FCS Management web application main directory: ``cd /vagrant/fcs``.

#. In first terminal:

    * create data base: ``python manage.py syncdb``,
    * apply data base migrations with ``python manage.py migrate``,
    * set Userena permissions: ``python manage.py check_permissions``,
    * start web application server: ``python manage.py runserver 192.168.0.2:8000`` on local port 8000.

#. In second terminal window start Autoscaling module: ``python manage.py autoscaling 192.168.0.2``.
#. Open browser and go to ``http://192.168.0.2:8000``.
#. Register new user. Activation mail should be displayed in console.
#. Log in.
#. Click :menuselection:`Tasks --> Add new`. Fill form. Confirm with :guilabel:`Add` button.
#. Crawling process will begin soon. You can monitor it in terminal's windows and logs of crawler and server located in :file:`./fcs/fcs`.
#. In task details(hyperlink in tasks table) you can download crawling results.