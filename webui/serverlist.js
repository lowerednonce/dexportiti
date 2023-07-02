"use strict"

let SERVER_ID = "";

async function read_local_slist() {
    try {
        const response = await fetch("../export.json");
        let json_data = await response.json();
        return json_data;
    } catch (error) {
        console.error("Error in retrieving server list: ", error);
        alert("There was an error reading the local server list.");
    }
}

function extract_server_icon_html(icon) {
    return "<img id=\"server-icon\" src=\"../" + SERVER_ID +  "/assets/" + icon.key + ".png" + "\"></img>"
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

function show_server(data) {

    // displaying server info
    const parse_list = [
        ["icon",         "",                extract_server_icon_html(data.icon)],
        ["name",         "",                data.name],
        ["id",           "server id: ",     data.id],
        ["created_at",   "creation date: ", convert_date(data["created-at"])],
        ["member_count", "member count: ",  data.members.length],
        ["locale",       "locale: ",        data.preferred_locale],
        ["filesize",     "filesize limit: ",data.filesize_limit/1024 + "Kb"],
        ["export-date",  "export's date: " ,convert_date(data["export-info"]["end-date"])]
    ];
    parse_list.map(pair => {
        document.getElementById(pair[0]).innerHTML = pair[1] + pair[2];
    });

    // loading user info
    const users_HTML = data["active-users"]
        .map( user => {
            return "<div class=\"active-member\">"
                + "<img loading=\"lazy\" class=\"active-member-img\" src=\"" + extract_avatar_url(user) + "\" width=\"64\" height=\"64\">"
                + "<p class=\"active-member-username\"><b>"+ user.name + "#" + user.discriminator + (user.bot ? " (bot)" : "") + "</b></p>"
                + "<p class=\"active-member-id\"><i>id: " + user.id + "</i></p>"
                + "<p class=\"active-member-created\">registered: " + convert_date(user.created_at) + "</p>"
                + "<p class=\"active-member-flags\">public flags: " + user.public_flags + "</p>"
                + "</div>";
        })
        .reduce((total, elem) => {
            return total + elem;
        });

    // loading the users HTML as to not bother with it the first time the button is clicked
    document.getElementsByClassName("users")[0].innerHTML = users_HTML;

    const emojis_HTML = data.emojis
        .map((emoji) => {
            console.log(emoji)
            return "<div class=\"emoji-div\">"
                     + "<div class=\"emoji-image\">"
                         + "<img loading=\"lazy\" src=\"" + extract_emoji_url(emoji) + "\" height=\"32\" width=\"32\" >"
                     + "</div>"
                     + "<p class=\"emoji-name\">:" + emoji.name + ":</p>"
                 + "</div>";
        })
        .reduce((total, elem) => {
            return total + elem;
        });

    document.getElementById("emojis").innerHTML = emojis_HTML;
}

read_local_slist().then(data => {
    console.info("parsed server data: ", data);

    data["servers"].map(server => {
        console.log("server option: ", server);
        document.getElementById("sselection-form-list").innerHTML += "<option value=\"" + server.id + "\">" + server.name + "</option>"
    });

})

const main = () => {

document.getElementById("sselection-form-btn").onclick = (e) => {

  e.preventDefault();

  SERVER_ID = document.getElementById("sselection-form-list").value
  console.log("working with server of id ", SERVER_ID);

  // load server JSON
  read_local_JSON("../" + SERVER_ID +"/core.json")
      .then(data => {
          console.log(data);
          Object.freeze(data);

          // server info
          show_server(data);

          // TODO: channels list
          /*
          // channel selection
          const channel_options_HTML = data.channels.map( chn => {
              return "<option value=\"" + chn.id + "\">" + chn.name + "</option>"
          })
          .reduce((total, elem) => {
              return total + elem;
          });

          document.getElementById("cselection-form-list").innerHTML = channel_options_HTML;

          document.getElementById("cselection-form-btn").onclick = gen_channel_selector(data, false);
          document.getElementById("fselection-form-btn").onclick = gen_channel_selector(data, true);
          */
      });
  }
}
