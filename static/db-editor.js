/* TOOLS */

function encodeRequest(data) {
    return encodeURIComponent(JSON.stringify(data))
}

function get_tables() {
    fetch(`${API_URL}?data=${encodeRequest({ command: 'get_tables' })}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            data.forEach(element => {
                button = document.createElement('input');
                button.type = 'button';
                button.value = element;
                button.onclick = function () { get_table_data(model = element) };
                tabs.appendChild(button);
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            alert('Error: ' + error.message);
        });
}



function create_content_header(data) {

    headerRow = document.createElement('div');
    headerRow.className = 'one-line header-row width-100';

    for (let [key, val] of Object.entries(data)) {
        header = document.createElement('p');
        header.innerHTML = key;
        headerRow.appendChild(header);
    }
    return headerRow;
}

function create_records(data) {
    const editor = document.querySelector('#content');

    data.forEach(row => {
        row_div = document.createElement('div');
        row_div.className = 'record_row';
        for (let [key, val] of Object.entries(row)) {
            if (val instanceof Array) {
                group_div = document.createElement('div');
                group_div.className = 'column';
                val.forEach(el => {
                    input = document.createElement('input');

                    if (el.support_id) { input.value = el.support_id; }
                    if (el.name) { input.value = el.name; }
                    if (el.full_name) { input.value = el.full_name; }
                    if (el.url) { input.value = el.url; }
                    if (el.email) { input.value = el.email; }



                    input.name = key;
                    group_div.appendChild(input);
                });
                row_div.appendChild(group_div);
            } else if (val instanceof Object) {
                input = document.createElement('input');
                if (val.name) { input.value = val.name; }
                if (val.full_name) { input.value = val.full_name; }
                input.name = key;
                row_div.appendChild(input);
            } else {
                input = document.createElement('input');
                input.value = val;
                input.name = key;
                if (key == "id" || key.includes('_id')) {
                    input.disabled = true;
                }
                row_div.appendChild(input);
            }
            //input.addEventListener("mouseup", onMouseUp, false);
            input.addEventListener("keypress", onSave, false);


        }


        editor.appendChild(row_div);
    });
}



function get_table_data(model) {
    const editor = document.querySelector('#content');
    const current_tab = document.querySelector('#current-tab')
    editor.innerHTML = '';
    current_tab.innerHTML = model;
    if (document.querySelector('[name="tasksExcl"]').checked) {
        exclude_list = ['tasks'];
    }
    else {
        exclude_list = [''];
    }

    fetch(`${API_URL}?data=${encodeRequest({ command: 'get_all', model: model, include: true, exclude: exclude_list})}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.length > 0) {
                editor.appendChild(create_content_header(data[0]));
                create_records(data);
            }

        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            alert('Error: ' + error.message);
        });
}





window.onload = () => {
    API_URL = 'http://104.197.195.100/api/v1';
    const editor = document.querySelector('#content');
    const tabs = document.querySelector('#tabs');

    get_tables();
}

function onSave(e) {
    if (e.key == "Enter") {
        const element = document.activeElement;
        record_row = element.closest('.record_row');
        record_id = record_row.firstChild.value;
        
        model = document.querySelector('#current-tab').textContent;


        updates = {};
        updates[element.name] = element.value;

        fetch(API_URL, {
            method: "POST",
            body: JSON.stringify(
                {
                    command: "update_one",
                    payload: {
                        model: model,
                        record_id: parseInt(record_id),
                        updates: updates
                    }
                }
            ),
            headers: {
                'Content-Type': 'application/json'
            }
        })
    }
}


























