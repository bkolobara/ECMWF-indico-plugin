// Hijack the setupCategoryDisplayEventList function to always load events in the future.
window._setupCategoryDisplayEventList = window.setupCategoryDisplayEventList;
window.setupCategoryDisplayEventList = function(_, showPastEvents) {
  window._setupCategoryDisplayEventList(true, showPastEvents);
  // In indico 2.0.3 we still don't have the showFutureEvents parameter
  // and we need to work around it.
  var $eventList = $(".event-list");
  var $futureEvents = $eventList.find(".future-events");
  $futureEvents
    .find(".js-toggle-list")
    .first()
    .trigger("click", true);
};

// Turn text into links inside the registration form
$(document).ready(function() {
  // If the page is displayed inside an iFrame then the header/footer is disabled.
  function inIframe() {
    try {
      return window.self !== window.top;
    } catch (e) {
      return true;
    }
  }
  if (inIframe()) {
    $("head link[rel='stylesheet']")
      .last()
      .after(
        "<style> \
  .event-page-header, .footer {display: none !important;} \
  </style>"
      );
  } else {
    $("head link[rel='stylesheet']")
      .last()
      .after(
        "<style> \
  .event-page-header, .footer {display: block !important;} \
  </style>"
      );
  }

  function linkifyForm() {
    $("span.ng-binding").linkify({
      target: "_blank"
    });
  }
  // The form is rendered on the frontend and we need to wait around 1 second before the element exist
  setTimeout(linkifyForm, 1000);
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
