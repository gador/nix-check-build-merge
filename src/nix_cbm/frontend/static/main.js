$(document).ready(function () {
  // flash an alert
  // remove previous alerts by default
  // set clean to false to keep old alerts
  function flash_alert (message, category, clean) {
    if (typeof clean === 'undefined') clean = true
    if (clean) {
      remove_alerts()
    }

    var htmlString =
      '<div class="alert alert-' + category + ' alert-dismissible">'
    htmlString +=
      '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">'
    htmlString +=
      '<span aria-hidden="true">&times;</span></button>' + message + '</div>'
    $(htmlString)
      .prependTo('#mainContent')
      .hide()
      .slideDown()
  }

  function remove_alerts () {
    $('.alert').slideUp('normal', function () {
      $(this).remove()
    })
  }

  function check_job_status (status_url, button) {
    $.getJSON(status_url, function (data) {
      console.log(data)
      switch (data.status) {
        case 'unknown':
          flash_alert('Unknown job id', 'danger')
          $('#' + button).removeAttr('disabled')
          break
        case 'finished':
          flash_alert(data.result, 'success')
          $('#' + button).removeAttr('disabled')
          break
        case 'failed':
          flash_alert('Job failed: ' + data.message, 'danger')
          $('#' + button).removeAttr('disabled')
          break
        default:
          // queued/started/deferred
          setTimeout(function () {
            check_job_status(status_url, button)
          }, 500)
      }
    })
  }

  // submit form
  $('#check').on('click', function () {
    flash_alert('Running hydra-check', 'info')
    $.ajax({
      url: $SCRIPT_ROOT + '/task/check',
      data: $('#taskForm').serialize(),
      method: 'POST',
      dataType: 'json',
      success: function (data, status, request) {
        $('#check').attr('disabled', 'disabled')
        flash_alert('Running hydra-check', 'info')
        var status_url = request.getResponseHeader('Location')
        check_job_status(status_url, 'check')
      },
      error: function (jqXHR, textStatus, errorThrown) {
        flash_alert(JSON.parse(jqXHR.responseText).message, 'danger')
      }
    })
  })

  $('#reload-maintainer').on('click', function () {
    flash_alert(
      'Reloading packages with ' + $('#reload-maintainer').val(),
      'info'
    )
    $.ajax({
      url: $SCRIPT_ROOT + '/task/maintainer',
      data: $('#taskForm').serialize(),
      method: 'POST',
      dataType: 'json',
      success: function (data, status, request) {
        $('#reload-maintainer').attr('disabled', 'disabled')
        flash_alert('Running hydra-check', 'info')
        var status_url = request.getResponseHeader('Location')
        check_job_status(status_url, 'reload-maintainer')
      },
      error: function (jqXHR, textStatus, errorThrown) {
        flash_alert(JSON.parse(jqXHR.responseText).message, 'danger')
      }
    })
  })
})
