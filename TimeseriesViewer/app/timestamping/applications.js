import {timeConverter} from "../../index.js";
import {getMongoURLfromUI, sendCORSrequest} from "./shared.js";

export function getApplicationsFromMongo(username, experiment_id) {
    "use strict";
    let endpoint = getMongoURLfromUI();
    let mongo_REST_endpoint =
        endpoint + "/tests" +
        "?where={%22experiment_id%22:%22" + experiment_id + "%22, %22username%22:%22" + username + "%22}";
    getApplicationsFromMongoPaginated(mongo_REST_endpoint, true)
}

function getApplicationsFromMongoPaginated(mongo_REST_endpoint, remove_previous) {
    let headers = [{"header": "Accept", "value": "application/json"}];
    sendCORSrequest("GET", mongo_REST_endpoint, headers, 200, function (response) {
        populateApplicationsDropdown(response, remove_previous);
        if (response._meta["page"] * response["_meta"]["max_results"] < response["_meta"]["total"]) {
            getApplicationsFromMongoPaginated(getMongoURLfromUI() + "/" + response["_links"]["next"]["href"], false);
        }
    }, "Error getting applications");
}


export function getApplicationTimes() {
    "use strict";
    let experiments_form = document.getElementById("experiment_picker");
    let application_label = experiments_form.elements.application;
    let application_id = application_label.application_id;

    let endpoint = getMongoURLfromUI();
    let headers = [{"header": "Accept", "value": "application/json"}];
    let mongo_REST_endpoint = endpoint + "/tests/" + application_id;

    sendCORSrequest("GET", mongo_REST_endpoint, headers, 200, function (response) {
        propagateApplicationTimes(response)
    }, "Error getting application times");
}

export function deleteApplication(application, check_confirm) {
    "use strict";
    if (check_confirm) {
        var r = confirm("Are you sure do you want to delete the test?");
        if (r === false) {
            return
        }
    }

    var experiments_form;
    var application_label;
    var application_id;
    var application_etag;

    if (application) {
        application_id = application.application_id;
        application_etag = application.etag;
    } else {
        experiments_form = document.getElementById("experiment_picker");
        application_label = experiments_form.elements.application;
        application_id = application_label.application_id;
        application_etag = application_label.etag;
    }

    let endpoint = getMongoURLfromUI();
    let mongo_REST_endpoint = endpoint + "/tests/" + application_id;

    let headers = [{"header": "Accept", "value": "application/json"}, {
        "header": "If-Match",
        "value": application_etag
    }];

    sendCORSrequest("DELETE", mongo_REST_endpoint, headers, 204, function (response) {

    }, "Error deleting application information");
}

function application_label_on_click() {
    "use strict";
    let experiments_form = document.getElementById("experiment_picker");
    let app_label = experiments_form.elements.application;
    app_label.value = this.label_value;
    app_label.application_id = this.application_id;
    app_label.etag = this.etag;
}

export function propagateApplicationTimes(application) {
    "use strict";
    let times = document.getElementById("times_form");
    times.elements.start_time.value = timeConverter(application.start_time);
    times.elements.end_time.value = timeConverter(application.end_time);
}

function populateApplicationsDropdown(applications, remove_previous) {
    "use strict";
    let list = document.getElementById("apps_timepicker_list");

    if (remove_previous) {
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }
    }
    for (let app of applications._items) {
        let child = document.createElement("li");

        var button1 = document.createElement("div");
        button1.innerHTML = "Set: " + app.test_name.bold();
        button1.classList = "btn btn-default ";
        button1.label_value = app.test_name;
        button1.application_id = app._id;
        button1.etag = app._etag;
        button1.onclick = application_label_on_click
        child.appendChild(button1);

        var button2 = document.createElement("div");
        button2.innerHTML = "Delete";
        button2.classList = "btn btn-default ";
        button2.application_id = app._id;
        button2.etag = app._etag;
        button2.onclick = deleteApplication
        child.appendChild(button2);

        list.append(child);
    }
}