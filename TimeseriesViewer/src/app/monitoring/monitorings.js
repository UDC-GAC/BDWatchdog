import {changeGraphValues, reDrawGraphByNumber, addGraph} from "./timeseries.js";
import {addFormFromFile} from "../../index.js";
import {getFormFromDiv, getNumFromForm, getTodayTime, getNowTime, setNowTime} from "../forms.js";
import {addReport} from "../reporting/reports.js";

import {formsContainerId} from "../../index.js";

// PUBLIC //
export let monitorings = []
export const divFormsIdBase = "monitorings-form_"

export function resetFormsList() {
    monitorings = []
}

export function addEmptyMetricsForm() {
    "use strict"
    addNewMetricsForm(default_metrics_form)
}

export function addNewMetricsForm(metrics_form) {
    "use strict"
    //let newArr = JSON.parse(metrics_form)
    //let timeseries = newArr["timeseries"]
    let timeseries = metrics_form["timeseries"]
    for (let plot of timeseries) {
        addFormFromFile(plot)
    }
}

export function change_datetime_ids() {
    "use strict"
    let datetime
    let newDate = new Date()
    let FiveMinutes = 5 * 60 * 1000
    let ago = newDate.getTime() - FiveMinutes
    let now = newDate.getTime()

    datetime = document.getElementById("datetimepicker0")
    datetime.id = divFormsIdBase + "_" + current_form_number + "_" + datetime.id

    newDate = new Date(ago)
    datetime.children[0].value = getTodayTime(newDate) + "-" + getNowTime(newDate)

    datetime = document.getElementById("datetimepicker1")
    datetime.id = divFormsIdBase + "_" + current_form_number + "_" + datetime.id

    newDate = new Date(now)
    datetime.children[0].value = getTodayTime(newDate) + "-" + getNowTime(newDate)
}

export function increase_form_counter() {
    form_counter = form_counter + 1
}

export function decrease_form_counter() {
    form_counter = form_counter - 1
}

export function addMetricsForm(metrics, yranges) {
    "use strict"
    //Create the form html
    let newdiv = document.createElement("div")
    let divIdName = divFormsIdBase + form_counter
    newdiv.setAttribute("id", divIdName)

    monitorings.push(newdiv)
    newdiv.className += " form"
    //current_form_number = form_counter
    let this_form_number = form_counter
    form_counter = form_counter + 1

    addGraph(metrics)
    addReport(metrics)

    //Add the new metrics form to the container
    let theContainer = document.getElementById(formsContainerId)
    theContainer.appendChild(newdiv)
    $("#" + newdiv.id).load(metrics_form_html_filename, function () {
        initializeForm(this_form_number, metrics, yranges)
    })

    //Return the number of this new metrics form
    return this_form_number
}

export function changeTimeValues(form, start_date, end_date) {
    "use strict"
    let graph_number = getNumFromForm(form)
    let metrics = readFormMetrics(form)
    changeGraphValues(graph_number, metrics, start_date, end_date)
}

export function readFormMetrics(form) {
    "use strict"
    let metricsHtml = form.getElementsByClassName("metric")
    let metrics = []
    for (let i = 0; i < metricsHtml.length; i++) {
        let metric = {}
        let metricHtml = metricsHtml[i]

        metric["aggregator"] = metricHtml.value.split(":")[0]
        metric["metric"] = metricHtml.value.split(":")[1]


        let tagsHtml = metricHtml.parentNode.getElementsByClassName("tag")
        let tags = []
        for (let j = 0; j < tagsHtml.length; j++) {
            tags.push(tagsHtml[j].value)
        }
        metric["tags"] = tags

        metrics.push(metric)
    }
    return metrics
}


export function refreshTimeNow(form) {
    let checkbox = form.elements.autoreload
    if (checkbox.checked) {
        let autoreload_time = form.elements.autoreload_time.value
        setTimeout(refreshTimeNow, autoreload_time * 1000, form)
        setNowTime(form, 1)
        drawTimeseries(form)
        handleReport(form)
    } else {
        setNowTime(form)
    }
}

export function drawTimeseries(form) {
    "use strict"
    let start_date = form.elements.datetime0.value
    let end_date = form.elements.datetime1.value
    let graph_number = getNumFromForm(form)

    let metrics = readFormMetrics(form)

    changeGraphValues(graph_number, metrics, start_date, end_date)
    reDrawGraphByNumber(graph_number)
}
window.drawTimeseries = drawTimeseries

export function addMetric(form, metric) {
    let metricsDiv = form.getElementsByClassName("monitorings-div")[0]

    if (metric === undefined) {
        metric = default_metric
    }

    let divList = get_list_from_element(metricsDiv)
    let tags = metric["tags"]
    let element = $("<div class=\"row metric-row\" ondragover=\"cancelDragOver()\">").load(metric_html_filename, function () {
        this.getElementsByTagName('input')[0].value = metric["aggregator"] + ":" + metric["metric"]
        for (let i = 0; i < tags.length; i++) {
            addTag(element[0], tags[i])
        }
    })
    element.appendTo(divList)
}
window.addMetric = addMetric

export function addTag(metric, tag) {
    let tagsDiv = metric.getElementsByClassName("tags-div")[0]

    if (tag === null) {
        tag = defaultTag
    }

    let divList = get_list_from_element(tagsDiv)
    let element = $("<div class=\"row tag-row\" ondragover=\"cancelDragOver()\">").load(tag_html_filename, function () {
        this.getElementsByTagName('input')[0].value = tag
    })
    element.appendTo(divList)
}
window.addTag = addTag

export function removeThisMetricOrTag(button) {
    let input = button.parentNode.children[0] //input of this button
    let aElements = button.parentNode.parentNode.getElementsByClassName("row")
    let aElementsLength = aElements.length
    for (let i = 0; i < aElementsLength; i++) {
        if (aElements[i] === button.parentNode) {
            button.parentNode.parentNode.removeChild(aElements[i])
            break
        }
    }
}
window.removeThisMetricOrTag = removeThisMetricOrTag

// PRIVATE //

let form_counter = 0
let current_form_number = 0
const tag_html_filename = "html/tag.html"
const metric_html_filename = "html/metric.html"
const metrics_form_html_filename = "html/monitorings_form.html"
const default_metric = {metric: "proc.cpu.user", aggregator: "zimsum", tags: ["host=node0", "command=YarnChild"]}
const default_metrics_form = "{\"timeseries\":[{\"metrics\":[{\"metric\":\"proc.cpu.user\",\"aggregator\":\"zimsum\",\"tags\":[\"host=node1\"]}],\"yranges\":{\"ymin\":0,\"ymax\":800}}]}"
const defaultTag = "host=node0"

function get_list_from_element(element) {
    for (let i = 0; i < element.children.length; i++) {
        if (element.children[i].tagName === "UL") {
            return element.children[i]
        }
    }
}


let initializeForm = function (form_number, metrics, yranges) {
    "use strict"
    let form = getFormFromDiv(document.getElementById(divFormsIdBase + form_number))
    for (let metric of metrics) {
        addMetric(form, metric)
    }
    form.elements.min_y.value = yranges.ymin
    form.elements.max_y.value = yranges.ymax
    form.elements.scaleY.checked = true


    let start_date = form.elements.datetime0.value
    let end_date = form.elements.datetime1.value
    let graph_number = getNumFromForm(form)

    changeGraphValues(graph_number, metrics, start_date, end_date)
}