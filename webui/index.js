"use strict";

let SERVER_ID = "";

async function read_local_JSON(filename) {
    try {
        const response = await fetch(filename);
        let json_data = await response.json();
        return json_data;
    } catch (error) {
        console.error('Error:', error);
    }
}

async function read_local_slist() {
    try {
        const response = await fetch("export.json");
        let json_data = await response.json();
        return json_data;
    } catch (error) {
        console.error("[Error] in retrieving server list: ", error);
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

function extract_attachments_html(attachments) {
    const attachments_HTML = attachments.map((e) => {
        const img_height = (parseInt(e["height"]) > 500 ) ? 500 : parseInt(e["height"])
        const img_width  = (parseInt(e["height"]) > 500 ) ? e["width"]/(parseInt(e["height"])/500): e["width"] 
        return ("<img loading=\"lazy\" src=\""
        + SERVER_ID + "/attachments/" + e["id"] + "-" + e["filename"]
        + "\" height=\"" + img_height + "\" width=\"" + img_width + "\""
        + " alt=\"" + e["filename"] + "\"></img>");
    })
    // .reduce((total, item) => {
    //     return total + item;
    // });
    return attachments_HTML;
}

function show_message_HTML(cmsg, users) {
    let cmsg_HTML = "<div class=\"cmsg-div\">"
    console.info(cmsg);
    let user = users.filter((u) => {
        return (u["id"] == cmsg["author"])
    });
    console.log(user);
    user = user[0];
    if(cmsg["type"] == "MessageType.new_member") {
        cmsg_HTML += "<p class=\"cmsg-content\"> " + "new member: " + user["name"] + " </p>"
        + "<p class=\"cmsg-timestamp\">(<i>" + convert_date(cmsg["created_at"]) + "</i>)</p>"
    } else {
        cmsg_HTML += "<div class=\"cmsg-sender\"><img src=\"" + extract_avatar_url(user) + "\" width=\"64\" height=\"64\"></img></div>"
        + "<p class=\"cmsg-content\">" + cmsg["content"].replaceAll("\n", "</br>") + (cmsg["edited_at"] == null ?  "" : " <i>(edited at " + convert_date(cmsg["edited_at"]) + ")</i>")
        + "<div class=\"cmsg-attachments\">" + extract_attachments_html(cmsg["attachments"])+ "</div>"
        + "</p><p class=\"cmsg-timestamp\">(<i>" + convert_date(cmsg["created_at"]) + "</i>)</p>"
    }
    cmsg_HTML += (cmsg["pinned"] ? "<p><b><i>(pinned)</i></b></p>" : "") + "</div><hr class=\"cmsg-break\">";
    return cmsg_HTML;
}

let show_members = () => {
    document.getElementById("hide-members").style.display = "flex";
    document.getElementById("show-members").style.display = "none";
    document.getElementsByClassName("users")[0].style.display = "flex";
}

let hide_members = () => {
    document.getElementById("hide-members").style.display = "none";
    document.getElementById("show-members").style.display = "flex";
    document.getElementsByClassName("users")[0].style.display = "none";
}

function gen_cmsg_counter(limit) {
    let counter = 0;
    return [(amount, e) => {
        e.preventDefault();
        if((counter+amount) > limit || (counter+amount)<0){
            console.error("failed to display more messages");
            console.info("counter at: ", counter, " amount at: ", amount, " limit at: ", limit);
            return
        }else {
            counter += amount;
        }
    },
        () => {return counter}
    ];
}

read_local_slist().then(data => {
    console.info(data);

    data["servers"].map(elem => {
        console.log(elem);
        document.getElementById("sselection-form-list").innerHTML += "<option value=\"" + elem["id"] + "\">" + elem["name"] + "</option>"
    });

})

function show_server(data) {
    // displaying server info
    const parse_list = [
        ["name",         "", data["name"] + (data["bot"] ? " (bot)" : "")],
        ["id",           "server id: ",     data["id"]],
        ["created_at",   "creation date: ", convert_date(data["created-at"])],
        ["member_count", "member count: ",   data["members"].length],
        ["locale",       "locale: ",         data["preferred_locale"]]
    ];
    parse_list.map(pair => {
        document.getElementById(pair[0]).innerHTML = pair[1] + pair[2];
    });

    // loading user info 
    const users_HTML = data["active-users"]
        .map( user => { 
           console.info(user);
            return "<div class=\"active-member\">"
                + "<img loading=\"lazy\" class=\"active-member-img\" src=\"" + extract_avatar_url(user) + "\" width=\"64\" height=\"64\">"
                + "<p class=\"active-member-username\"><b>"+ user["name"] + "#" + user["discriminator"] + (user["bot"] ? " (bot)" : "") + "</b></p>"
                + "<p class=\"active-member-id\"><i>id: " + user["id"] + "</i></p>"
                + "<p class=\"active-member-created\">registered: " + convert_date(user["created_at"]) + "</p>"
                + "<p class=\"active-member-flags\">public flags: " + user["public_flags"] + "</p>"
                + "</div>";
        })
        .reduce((total, elem) => {
            return total + elem;
        });

    // loading the users HTML as to not bother with it the first time the button is clicked
    document.getElementsByClassName("users")[0].innerHTML = users_HTML; 
}

function gen_channel_selector(data) {
    // clojures to get the data object into another lexical scope
    return (e) => {

        e.preventDefault();

        const chn_id = document.getElementById("cselection-form-list").value;
        console.log("working with channel id: ", chn_id);

        const chn = data["channels"].filter((i) => {
            return (i["id"] == chn_id)
        })[0]

        console.log(chn);

        const parse_list = [
                ["cname", "channel name: ",                         chn["name"] + " (" + chn["type"] + ")" ],
                ["cdesc", "channel desciption: ",                   chn["topic"]??"<i>not provided</i>"],
                ["cnsfw", "NSFW: ",                                 chn["nsfw"] ],
                ["cid",   "id: ",                                   "<i>" + chn["id"] + "</i>"],
                ["ccreated", "created: ",                           convert_date(chn["created_at"])],
                ["cmsg_count", "total message count: ",             (chn["messages"]??0).length],
                ["cmsg_thread_archive", "Thread archive default: ", chn["default_auto_archive_duration"]/60 +" minutes"],
                ["cmsg_news", "News: ",                             (chn["is_news"] ? "yes" : "no")]
        ]

        parse_list.map((line) => {
            document.getElementById(line[0]).innerHTML = line[1] + line[2];
        });

        if(chn['type'] == "text") {

            const cmsg_counters = gen_cmsg_counter(chn["messages"].length);
            const cmsg_counter_setter = cmsg_counters[0];
            const cmsg_counter_getter = cmsg_counters[1];

            // console.info((chn["messages"]) == (chn["messages"].sort((e,p) => {return e["created_at"]>["created_at"]})))
            
            
            const render_cmsg = () => {
                console.log("render called");
                console.log("slicing from ", cmsg_counter_getter(), " till ", cmsg_counter_getter()+50);
                document.getElementById("cmsg").innerHTML = chn["messages"]
                .sort((e,p) => {
                    return e["created_at"]>p["created_at"];
                })
                .slice(cmsg_counter_getter(),cmsg_counter_getter()+50)
                .map((e) => {
                    return show_message_HTML(e, data["active-users"]);
                })
                .reduce((total, e) => {
                    return total+e;
                });
            };


            render_cmsg();
            // document.getElementById("cmsg").innerHTML += "<button id=\"cmsg-btn\">add more</button>";
            
            document.getElementById("cmsg-btn-up").onclick = (e) => {
                cmsg_counter_setter(50, e);
                render_cmsg();
                document.getElementsByClassName("channel-information")[0].scrollIntoView({behavior: "smooth"});
            };
            
            document.getElementById("cmsg-btn-down").onclick = (e) => {
                cmsg_counter_setter(-50, e);
                render_cmsg();
                document.getElementById("cmsg-bottom").scrollIntoView({behavior: "smooth"});
            };       

        }

    }
}

const main = () => {

// main function so that the page is fully loaded

document.getElementById("sselection-form-btn").onclick = (e) => {

    e.preventDefault();

    SERVER_ID = document.getElementById("sselection-form-list").value
    console.log("working with server of id ", SERVER_ID);

    // load server JSON
    read_local_JSON("../" + SERVER_ID +"/core.json")
        .then(data => {
            console.log(data);

            // server info
            show_server(data);
            
            // channel selection
            const channel_options_HTML = data["channels"].map( chn => {
                return "<option value=\"" + chn["id"] + "\">" + chn["name"] + "</option>"
            })
            .reduce((total, elem) => {
                return total + elem;
            });

            document.getElementById("cselection-form-list").innerHTML = channel_options_HTML;

            document.getElementById("cselection-form-btn").onclick = gen_channel_selector(data);

        });
}

};
