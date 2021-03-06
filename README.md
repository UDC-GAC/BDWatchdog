# BDWatchdog

<p align="center">
  <img src="https://s3-eu-west-1.amazonaws.com/jonatan.enes.udc/bdwatchdog_website/logo_bdwatchdog.png" width="150" title="Logo">
</p>


This repository acts as an umbrella project for different subprojects 
that can be combined to create **BDWatchdog**, a monitoring and profiling framework 
capable of producing resource usage information on a process-level 
as well as detailed profiling of Java-based applications in the form 
of flame graphs. In addition, auxiliar tools have been developed such 
as a web application to visualize the data generated and a timestamp generator used to bound experimentation runs.

Thanks to the **_process-based monitoring_** approach, this framework can be 
deployed on newer virtualization technologies like **_containers_**, acting 
as a base for other projects that may need real-time container resource 
monitorization.

* If you need more information regarding the process-level monitoring 
check out the [MetricsFeeder](https://github.com/JonatanEnes/BDWatchdog/tree/master/MetricsFeeder)
subproject.

* If you want to know more about real-time java profiling with flame 
graphs, check out the [FlamegraphsGenerator](https://github.com/JonatanEnes/BDWatchdog/tree/master/FlamegraphsGenerator)
subproject.

* If you want to know how many of the plots presented on this umbrella 
project have been generated, you can check out the 
[TimeseriesViewer](https://github.com/JonatanEnes/BDWatchdog/tree/master/TimeseriesViewer) 
subproject, which hosts a web application to visualize the time series 
data generated by the MetricsFeeder subproject and the flame graphs 
created from the data of the FlamegraphsGenerator subproject, as well 
as other utilities such as integration with the timestamping service.

* If you want to know more about the timestamp generation used to 
delimit the time duration of experiments and tests, visit the 
[TimestampsSnitch](https://github.com/JonatanEnes/BDWatchdog/tree/master/TimestampsSnitch)
subproject.


## About
BDWatchdog has been developed in the Computer Architecture 
Group at the University of A Coruña by Jonatan Enes (jonatan.enes@udc.es), 
Roberto R. Expósito and Juan Touriño.

For more information on this project you can visit its 
[webpage](http://bdwatchdog.dec.udc.es/monitoring/index.html) or 
even read the full length journal 
[article](https://www.sciencedirect.com/science/article/pii/S0167739X17316096) 
published in Future Generation Computer Systems (FGCS).
