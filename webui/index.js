"use strict";

const SERVER_ID = "1037637575239815220";

async function read_local_JSON(filename) {
    try {
        const response = await fetch(filename);
        let json_data = await response.json();
        return json_data;
    } catch (error) {
        console.error('Error:', error);
    }
}

function convert_date(timestamp){
    const date = new Date(parseInt(timestamp)*1000)
    return ("0" + date.getDate()).slice(-2)     + "/"
        + ("0" + (date.getMonth()+1)).slice(-2) + "/"
        + date.getFullYear()                    + " "
        + ("0" + date.getHours()).slice(-2)     + ":"
        + ("0" + date.getMinutes()).slice(-2)   + ":"
        + ("0" + date.getSeconds()).slice(-2);
    // DD/MM/YYYY HH:MM:SS
    // the ("" + part).slice(-2) is to add a leading zero
    // if it doesn't need a leading zero, it is sliced out
}

function extract_avatar_url(user) {
    if(user["avatar"] != null) {
        return SERVER_ID + "/assets/" + user["avatar"]["key"] + ".png"
    } else {
        return SERVER_ID + "/assets/" + user["default_avatar"]["key"] + ".png"
    }
}

let show_members;
let hide_members = () => {
    document.getElementById("hide-members").style.display = "none";
    document.getElementById("show-members").style.display = "flex";
    document.getElementsByClassName("users")[0].style.display = "none";
}

read_local_JSON("../" + SERVER_ID +"/core.json")
    .then(data => {
        console.log(data);
        const parse_list = [
            ["name",         data["name"]],
            ["id",           data["id"]],
            ["created_at",   convert_date(data["created-at"])],
            ["member_count", data["members"].length],
            ["locale",       data["preferred_locale"]]
        ];
        parse_list.map(pair => {
            document.getElementById(pair[0]).innerHTML += pair[1];
        });

        const users_HTML = data["active-users"]
            .map( user => { 
               console.info(user);
                return "<div class=\"active-member\">"
                    + "<img loading=\"lazy\" class=\"active-member-img\" src=\"" + extract_avatar_url(user) + "\" width=\"64\" height=\"64\">"
                    + "<p class=\"active-member-username\"><b>"+ user["name"] + "#" + user["discriminator"] + "</b></p>"
                    + "<p class=\"active-member-id\"><i>id: " + user["id"] + "</i></p>"
                    + "<p class=\"active-member-created\">registered: " + convert_date(user["created_at"]) + "</p>"
                    + "</div>";
            })
            .reduce((total, elem) => {
                return total + elem;
            });
        
        document.getElementsByClassName("users")[0].innerHTML = users_HTML; 

        show_members = () => {
            document.getElementById("hide-members").style.display = "flex";
            document.getElementById("show-members").style.display = "none";
            document.getElementsByClassName("users")[0].style.display = "flex";
        }
        
    });
