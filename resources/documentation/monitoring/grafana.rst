=======
Grafana
=======

In this topic, we will see how to install graph_tool, using the provided rpms.

Installation
============

Install
-------

ansible role
^^^^^^^^^^^^

Using the ansible role prometheus_exporter, you can install grafana with the following command:

simply run ::

    ansible-playbook /etc/ansible/playbooks/<your playbook> --tags prometheus_client

manual installation
^^^^^^^^^^^^^^^^^^^

There is a packet for grafana-7 under /var/www/html/repositories/redhat/8.1/x86_64/custom/Packages/

so by running the following command:

    yum install grafana

it should install grafana-server.

Useful Files
------------

The service is located under /usr/lib/systemd/system/grafana-server.service

the binary under /usr/sbin/grafana-server

grafana datas (dashboards, and so on) under /var/lib/grafana/grafana.db

grafana default settings under /usr/share/grafana/conf/default.ini


Dashboard
=========

create dashboard
----------------

Query
^^^^^


metrics field
"""""""""""""

This section is where you put prometheus metric queries.
See the prometheus section of the doc for more info about the metrics (functions, different types of variables, show only certain instances)

.. image:: monitoring/capture/grafana/supp1.PNG
   :width: 80 %

By default, it shows you the requested metric in a graph panel.

.. image:: monitoring/capture/grafana/supp2.PNG
   :width: 80 %


legend field
""""""""""""



here, you can choose what the legend will look like.
.. note::

    syntaxe: {{ metric label }}text_you_want

by default, it will show the whole metric.
example:


.. image:: monitoring/capture/grafana/legend_field1.PNG
   :width: 60 %


example : {{instance}}:toto:{{device}}
you get:

.. image:: monitoring/capture/grafana/legend_field2.PNG
   :width: 30 %


min step and resolution
"""""""""""""""""""""""

.. note::

    it is recommended not to change the min step and Resolution

format
""""""

time series or table or heatmap
it is recommended to choose timeseries if you want to make a graph


instant
"""""""

if you only want to have the latest scraped metric.
Usefull when using tables


Transform
^^^^^^^^^

.. note::

    the transform tab is new with grafana7, and is still in development


.. image:: monitoring/capture/grafana/transform1.PNG
   :width: 30 %


Mainly usefull when using graphs
allows you to show the things you want in the table, by reducing, filtering, joining metrics, and organizing fields.


for example :


.. image:: monitoring/capture/grafana/transformExmemple.PNG
   :width: 50 %


here, we have 3 queries, but if you make no transform, it will look like this:


.. image:: monitoring/capture/grafana/transformExmemple3.PNG
   :width: 80 %

so we need to make the following transformations to get the desired table:

1. Filter by name, to only take the values that we want
2. Outer Join, to join the query values into one table (query A,query B,query C) here we join on ifName because it's the common value between the queries that we want   to use.
3. Organize field, to put everything where we want, and to rename de fields Value B and Value C (values of the queries)  to show what they represent.

with this transformation:

.. image:: monitoring/capture/grafana/transformExmemple2.PNG
   :width: 80 %

you get the following result:

.. image:: monitoring/capture/grafana/supp3.PNG
   :width: 80 %

you can find more about the different transformations here: https://grafana.com/docs/grafana/latest/panels/transformations/

Alert
^^^^^

you can create alerts in grafana, by setting up conditions. It is pretty much self explanatory, but if you want more info, you can check this link: https://grafana.com/docs/grafana/latest/alerting/create-alerts/



Types of Visualization
======================

By default, there are 11 different types of visualization, but you can install more using the plugin list.
You can find them here: https://grafana.com/grafana/plugins?direction=asc&orderBy=weight&type=panel

In this documentation, we will go through 2 of the most used ones, as they have approximately all the options that other types of visualization have.

Graph
-----

Panel
^^^^^

Display
"""""""

Here, you can choose the design of your graph. You can fidget with the options to get your desired graph.
If you want more info, check https://grafana.com/docs/grafana/latest/panels/visualizations/graph-panel/

Series override
"""""""""""""""

In this section, you have access to even more customization. It allows you to customize only certain series, using regex.
Here is a detailed example on how to use it: https://community.grafana.com/t/advanced-graphing-part1-style-overrides/207


Axes
""""

Choose the units of the axes, and relabel them. You can also add mins and maxs.
You can have more info here:


Legend
""""""

Legend related options, you can show the legend as a table, add min,max,avg,current values.

.. image:: monitoring/capture/grafana/LegendExemple.PNG
   :width: 80 %


Thresholds
""""""""""

The threshold lets you change the background color when the value is less than or greater than the chosen value.

.. image:: monitoring/capture/grafana/thresholdexemple1.PNG
   :width: 80 %


Time regions
""""""""""""

Allows to highlight certain time regions of the graph, not used very often

Data links, links
"""""""""""""""""

Here, you can add links to different graphs, using the URL.
For more info, check here: https://grafana.com/docs/grafana/latest/linking/data-links/

Bar gauge
---------

Panel
^^^^^

Display
"""""""

You can choose between two options in the show option.
Calculate will show you the result of the calculation (First Value, Last Value, and so on), whereas All Values will show you all the values scraped inthe last XX minutes. you can choose the max number of results in the Limit field.
You can also choose  the orientation and the display mode (aesthetics)

.. image:: monitoring/capture/grafana/BarGaugeex1.PNG
   :width: 80 %


Links
"""""

Cf above

Repeat options
""""""""""""""

If activated, will show the panel X times in the dashboard, with X being the number of results we get.

for example with the repeat option enabled:

.. image:: monitoring/capture/grafana/BarGaugeex2.PNG
   :width: 80 %

without the repeat option enabled:

.. image:: monitoring/capture/grafana/BarGaugeex3.PNG
   :width: 50 %

as you can see, in one case, you get the results in different panels, and in the other case you get the results in the same panel.



Field
^^^^^

Unit
""""

Self explanatory, choose the unit, min, max and the display name for the values.

Thresholds
""""""""""

Changes the color of the bars according to what is put in the threshold.

Ex:

.. image:: monitoring/capture/grafana/thresholdexemple2.PNG
   :width: 80 %

Value mapping
"""""""""""""

Transforms the values into text.

Ex:

.. image:: monitoring/capture/grafana/ValueMappingEx.PNG
   :width: 80 %

here, we know that if the metric's value is 1, it means that it is up, 2 down, and so on
So we map those values accordingly.


Data links
""""""""""

See above


Override
^^^^^^^^

Override lets you override some values, by filtering fields.
However, it is still a beta option.

for more info check above


Extra
=====

Variables
^^^^^^^^^

To access get variables like these:

.. image:: monitoring/capture/grafana/Captureshow.PNG
   :width: 30 %


first, go to the top right corner of grafana:


.. image:: monitoring/capture/grafana/variable.PNG
   :width: 30 %



go to variable


.. image:: monitoring/capture/grafana/Variable1.PNG
   :width: 20 %


Then, enter a query to get the results you want to transform as a variabe.
For exemple:

.. image:: monitoring/capture/grafana/variable2.PNG
   :width: 30 %

by doing this query you get the different instances of ifOutOctets.
without the regex used like that

.. image:: monitoring/capture/grafana/variable3.PNG
   :width: 80 %


you should get results like that:


.. image:: monitoring/capture/grafana/variable4.PNG
   :width: 50 %

however, by using the regex seen above, we get results that can be later used with some queries, like for example ::

    ifConnectorPresent{ifName=~"$interface"}

with $interface the name of our variable.

.. note::

    here, we use =~ in order to accept special regex caracters, like .* for example. You can see more about that in the prometheus part of the documentation


Main Dashboard
^^^^^^^^^^^^^^

To create a main dashboard, simply create a new dashboard, a choose visualisation style "Dashboard list"
you should get something like that:

.. image:: monitoring/capture/grafana/MainDashboard.PNG
   :width: 20 %

choose the Search option
and then simply choose the folder that you want to list.

.. image:: monitoring/capture/grafana/mainDashboard2.PNG
   :width: 80 %

by clicking on the dashboard links, you get redirected to them.
