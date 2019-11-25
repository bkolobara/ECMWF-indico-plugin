import linkifyElement from "linkifyjs/element";

import "./global.scss";
import "./timetable.scss";
import "./timetable_print.scss";
import "./ecmwf.scss";

// Point the abstract pdf generation link inside the "Call for Abstracts" menu
// in the management area to our custom abstract html page
$(document).ready(function() {
  var download_links = $('a[href$="book-of-abstracts.pdf"]').get();
  if (download_links.length > 0) {
    var download_link = download_links[0];
    var regex = /event\/(\d+)\/book-of-abstracts\.pdf/;
    var event_id = download_link.href.match(regex)[1];
    var new_download_url = "/ecmwf" + "/event/" + event_id + "/abstracts";
    download_link.href = new_download_url;
    download_link.target = "_blank";
  }
});

// Turn text into links inside the registration form
$(document).ready(function() {
  function linkifyForm() {
    document.querySelectorAll("span.ng-binding").forEach(el => linkifyElement(el));
  }
  // The form is rendered on the frontend and we need to wait around 2 second before the element exist
  setTimeout(linkifyForm, 2000);
});

// Google analytics
(function(w, d, s, l, i) {
  w[l] = w[l] || [];
  w[l].push({
    "gtm.start": new Date().getTime(),
    event: "gtm.js"
  });
  var f = d.getElementsByTagName(s)[0],
    j = d.createElement(s),
    dl = l != "dataLayer" ? "&l=" + l : "";
  j.async = true;
  j.src = "//www.googletagmanager.com/gtm.js?id=" + i + dl;
  f.parentNode.insertBefore(j, f);
})(window, document, "script", "dataLayer", "GTM-P5T597");
