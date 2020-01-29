import {changeTimeInputs, getFormFromDiv, getNumFromForm} from "./app/forms.js";
import {getGraphNumFromID, getGraphID, triggerResize} from "./app/graphs.js";

import {
    addNewMetricsForm,
    changeTimeValues,
    addMetricsForm,
    refreshTimeNow,
    resetFormsList,
    decrease_form_counter
} from "./app/monitoring/monitorings.js";
import {reDrawGraphByNumber, decrease_graph_counter} from "./app/monitoring/timeseries.js";
import {monitorings, divFormsIdBase} from "./app/monitoring/monitorings.js";

import {profilings} from "./app/profiling/profilings.js";
import {decrease_report_counter} from "./app/reporting/reports.js";

import {flameGraphsIdBase} from "./app/profiling/flamegraphs.js";

import {getExperimentsFromMongo, getExperimentTimes, deleteExperiment} from "./app/timestamping/experiments.js";
import {
    propagateApplicationTimes,
    getApplicationsFromMongo,
    getApplicationTimes,
    deleteApplication
} from "./app/timestamping/applications.js";
import {getNowTime, getTodayTime} from "./app/forms.js";

// PUBLIC //
export const formsContainerId = "formsContainer";
export const graphsContainerId = "graphsContainer";
export const reportsContainerId = "reportsContainer";
export const defaultExperimentsInfoURL = "http://bdwatchdog-demo:8000";

export function createCORSRequest(method, url) {
    "use strict";
    let xhr = new XMLHttpRequest();
    if ("withCredentials" in xhr) {
        // Check if the XMLHttpRequest object has a "withCredentials" property.
        // "withCredentials" only exists on XMLHTTPRequest2 objects.
        xhr.open(method, url, true)

    } else if (typeof XDomainRequest !== "undefined") {
        // Otherwise, check if XDomainRequest.
        // XDomainRequest only exists in IE, and is IE's way of making CORS requests.
        xhr = new XDomainRequest();
        xhr.open(method, url)
    } else {
        // Otherwise, CORS is not supported by the browser.
        xhr = null
    }
    return xhr
}

export function requestGraphRedraw(formID, graphX, graphY) {
    "use strict";
    if (graphX >= 300 && graphY >= 300) {
        let graphID;
        if (formID.startsWith("monitorings")) {
            graphID = getGraphID(getGraphNumFromID(formID));
            triggerResize(graphID, graphX, graphY)
        } else if (formID.startsWith("profiling")) {
            graphID = flameGraphsIdBase + formID.split("_")[1];
            triggerResize(graphID, graphX, graphY)
        }
    }
}

export function timeConverter(UNIX_timestamp) {
    "use strict";
    let a = new Date(UNIX_timestamp * 1000);
    let year = a.getFullYear();
    let month = a.getMonth() + 1;
    let date = a.getDate();
    let hour = a.getHours();
    let min = a.getMinutes();
    let sec = a.getSeconds();
    return year + "/" +
        ((month < 10) ? "0" : "") + month + "/" +
        ((date < 10) ? "0" : "") +
        date + "-" + ((hour < 10) ? "0" : "") +
        hour + ":" + ((min < 10) ? "0" : "") +
        min + ":" +
        ((sec < 10) ? "0" : "") + sec
}

export function getExperiments() {
    "use strict";
    let list = document.getElementById("exps_timepicker_list");
    list.insertAdjacentHTML("beforeend", "<div class=\"loader\"></div>");
    getExperimentsFromMongo(document.getElementById("experiment_picker").elements.username.value);

    let propagateAppsTimesButton = document.getElementById("propagateAppsTimesButton");
    propagateAppsTimesButton.disabled = true;

    let propagateExperimentsTimesButton = document.getElementById("propagateExperimentsTimesButton");
    propagateExperimentsTimesButton.disabled = false;

    let pickAppButton = document.getElementById("pickAppButton");
    pickAppButton.disabled = false

}

export function getApplications() {
    "use strict"
    let list = document.getElementById("apps_timepicker_list")
    list.insertAdjacentHTML("beforeend", "<div class=\"loader\"></div>")
    let username = document.getElementById("experiment_picker").elements.username.value
    let experiment = document.getElementById("experiment_picker").elements.experiment.value
    getApplicationsFromMongo(username, experiment)

    let propagateAppsTimesButton = document.getElementById("propagateAppsTimesButton")
    propagateAppsTimesButton.disabled = false
}


export function addFormFromFile(form_info) {
    "use strict"
    let metrics = form_info.metrics
    let yranges = form_info.yranges
    let new_form_number = addMetricsForm(metrics, yranges)
    return divFormsIdBase + new_form_number
}

export function loadFile() {
    "use strict"
    let input, file, fr

    if (typeof window.FileReader !== "function") {
        alert("The file API isn't supported on this browser yet.")
        return
    }

    input = document.getElementById("fileinput")
    if (!input) {
        alert("Um, couldn't find the fileinput element.")
    } else if (!input.files) {
        alert("This browser doesn't seem to support the `files` property of file inputs.")
    } else if (!input.files[0]) {
        alert("Please select a file before clicking 'Load'")
    } else {
        file = input.files[0]
        fr = new FileReader()
        fr.onload = receivedText
        fr.readAsText(file)
    }

    function receivedText(e) {
        let lines = e.target.result
        try {
            for (let form of JSON.parse(lines).timeseries) {
                addFormFromFile(form)
            }
        } catch (e) {
            alert(e) // error in the above string (in this case, yes)!
        }
    }
}

export function resizeAll() {
    "use strict"
    let sizes = document.getElementById("sizes_form")
    let sizeX = sizes.elements.graphX.value
    let sizeY = sizes.elements.graphY.value

    for (let form of monitorings) {
        requestGraphRedraw(form.id, sizeX, sizeY)
        handleReport(getFormFromDiv(document.getElementById(form.id)))
    }

    for (let profile of profilings) {
        requestGraphRedraw(profile.id, sizeX, sizeY)
    }
}

export function retimeAll() {
    "use strict"
    let times = document.getElementById("times_form"),
        time_start = times.elements.global_start_time.value,
        time_end = times.elements.global_end_time.value

    if (time_end === "NaN/NaN/NaN-NaN:NaN:NaN") {
        let newDate = new Date()
        time_end = getTodayTime(newDate) + "-" + getNowTime(newDate)
    }

    for (let form of monitorings) {
        requestGraphTimeRedraw(form.id, time_start, time_end)
        handleReport(getFormFromDiv(document.getElementById(form.id)))
    }

    for (let profile of profilings) {
        requestGraphTimeRedraw(profile.id, time_start, time_end) //FIXME
    }
}

export function autoreloadAll() {
    "use strict"

    for (let f of monitorings) {
        let form = getFormFromDiv(document.getElementById(f.id))
        if (form.elements.autoreload.checked === true) {
            form.elements.autoreload.checked = false
        } else {
            setAutoReload(f.id)
        }
    }
}

export function drawAllTimeseries() {
    "use strict"
    for (let form of monitorings) {
        requestGraphTimeRedraw(form.id)
    }
}

function requestGraphTimeRedraw(formID, start_time, end_time) {
    "use strict"
    let graph_num
    let form
    if (formID.startsWith("monitorings")) {
        graph_num = getGraphNumFromID(formID)
        form = getFormFromDiv(document.getElementById(formID))
        if (typeof start_time !== "undefined" && typeof end_time !== "undefined") {
            changeTimeValues(form, start_time, end_time)
            changeTimeInputs(form, start_time, end_time)
        }
        reDrawGraphByNumber(graph_num)
    }
    if (formID.startsWith("profiling")) {
        //graphID = flameGraphsIdBase + formID.split("_")[1];
        form = getFormFromDiv(document.getElementById(formID))
        changeTimeInputs(form, start_time, end_time)
    }
}

function setAutoReload(formID) {
    "use strict"
    let graphID
    if (formID.startsWith("monitorings")) {
        graphID = getGraphID(getGraphNumFromID(formID))
        let form = getFormFromDiv(document.getElementById(formID))
        form.elements.autoreload.checked = true
        let graph_number = getGraphNumFromID(graphID)
        reDrawGraphByNumber(graph_number)
        refreshTimeNow(form)
        handleReport(form)
    }
}

//----------------------
//--  DEMO specific -----

let spark_example = {
    label_exp: "Spark",
    label_app: "PageRank",
    end_time: 1512667973,
    start_time: 1512666728,
    type: "bdwatchdog"
};
window.spark_example = spark_example

let hadoop_example = {
    label_exp: "Hadoop",
    label_app: "TeraSort",
    end_time: 1512664138,
    start_time: 1512663747,
    type: "bdwatchdog"
};
window.hadoop_example = hadoop_example

let serverless_example = {
    label_exp: "serverless_experiments",
    label_app: "TeraSort_PageRank",
    end_time: 1567369745,
    start_time: 1567366402,
    type: "serverless"
};
window.serverless_example = serverless_example

let energy_example = {
    label_exp: "energy_experiments",
    label_app: "Metagenomics",
    end_time: 1571593092,
    start_time: 1571588317,
    type: "serverless"
};
window.energy_example = energy_example

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

hideForms()

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
    let container = document.getElementById(formsContainerId)
    while (container.firstChild) {
        container.removeChild(container.firstChild);
        decrease_form_counter()
    }
    resetFormsList()
    container = document.getElementById(graphsContainerId)
    while (container.firstChild) {
        container.removeChild(container.firstChild);
        decrease_graph_counter()
    }
    container = document.getElementById(reportsContainerId)
    while (container.firstChild) {
        container.removeChild(container.firstChild);
        decrease_report_counter()
    }
}
//--  DEMO specific -----
//----------------------

window.autoreloadAll = autoreloadAll
window.resizeAll = resizeAll
window.retimeAll = retimeAll
window.drawAllTimeseries = drawAllTimeseries
window.loadFile = loadFile


window.getExperiments = getExperiments
window.getExperimentTimes = getExperimentTimes
window.deleteExperiment = deleteExperiment
window.getApplications = getApplications
window.getApplicationTimes = getApplicationTimes
window.deleteApplication = deleteApplication
window.drawSomething = drawSomething


