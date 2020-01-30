import {
    addNewMetricsForm,
    resetFormsList,
    decrease_form_counter
} from "./app/monitoring/monitorings.js";
import {decrease_graph_counter} from "./app/monitoring/timeseries.js";
import {decrease_report_counter} from "./app/reporting/reports.js";

import {
    propagateApplicationTimes
} from "./app/timestamping/applications.js";


import {
    formsContainerId,
    graphsContainerId,
    reportsContainerId,
} from "./index.js";

let spark_example = {
    label_exp: "Spark",
    label_app: "PageRank",
    end_time: 1512667973,
    start_time: 1512666728,
    type: "bdwatchdog"
};
window.spark_example = spark_example;

let hadoop_example = {
    label_exp: "Hadoop",
    label_app: "TeraSort",
    end_time: 1512664138,
    start_time: 1512663747,
    type: "bdwatchdog"
};
window.hadoop_example = hadoop_example;

let serverless_example = {
    label_exp: "serverless_experiments",
    label_app: "TeraSort_PageRank",
    end_time: 1567369745,
    start_time: 1567366402,
    type: "serverless"
};
window.serverless_example = serverless_example;

let energy_example = {
    label_exp: "energy_experiments",
    label_app: "Metagenomics",
    end_time: 1571593092,
    start_time: 1571588317,
    type: "serverless"
};
window.energy_example = energy_example;

function set_timestamping_endpoint_value(endpoint) {
    document.getElementById("experiment_picker").elements.endpoint.value = endpoint
}

function set_opentsdb_endpoint_value(endpoint) {
    document.getElementById("config_form").elements.endpoint_OpenTSDB.value = endpoint
}

function hideForms() {
    let hideFormsButton = document.getElementById("forms-toggle");
    hideFormsButton.click();
}

export function drawSomething(forms, example) {
    "use strict";
    set_timestamping_endpoint_value("http://dante.dec.udc.es:8080/" + example.type + "/times/");
    set_opentsdb_endpoint_value("http://dante.dec.udc.es:8080/" + example.type + "/tsdb/");

    propagateApplicationTimes({end_time: example.end_time, start_time: example.start_time});
    cleanAll();
    addNewMetricsForm(forms);

    //TO BE FIXED //
    //waitForElement("#metrics-form_3", function(){
    //let reTimeButton = document.getElementById("reTimeButton")
    //reTimeButton.click()
    //});

    setTimeout(function () {
        let reTimeButton = document.getElementById("reTimeButton");
        reTimeButton.click();
    }, 1400);
    //TO BE FIX //

    let experiments_form = document.getElementById("experiment_picker");
    let experiment_label = experiments_form.elements.experiment;
    experiment_label.value = example.label_exp;
    let app_label = experiments_form.elements.application;
    app_label.value = example.label_app;
}

function cleanAll() {
    let container = document.getElementById(formsContainerId);
    while (container.firstChild) {
        container.removeChild(container.firstChild);
        decrease_form_counter()
    }
    resetFormsList();
    container = document.getElementById(graphsContainerId);
    while (container.firstChild) {
        container.removeChild(container.firstChild);
        decrease_graph_counter()
    }
    container = document.getElementById(reportsContainerId);
    while (container.firstChild) {
        container.removeChild(container.firstChild);
        decrease_report_counter()
    }
}
window.drawSomething = drawSomething;


// EXECUTION

hideForms();

jQuery.getJSON('app/templates/json/hadoop.json', function(data) {
    window.YarnChilds_form = data
});
jQuery.getJSON('app/templates/json/spark.json', function(data) {
    window.SparkExecutors_form = data
});
jQuery.getJSON('app/templates/json/metagenomic.json', function(data) {
    window.energy_form = data
});
jQuery.getJSON('app/templates/json/serverless.json', function(data) {
    window.serverless_form = data
});



