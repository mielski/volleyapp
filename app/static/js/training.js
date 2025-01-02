function get_training_id() {
    // Gets the training id from the url
    var path = window.location.pathname;
    return path.split("/")[2]
}

function update_button_status() {
    // ensure the first move-up button and last move-down button is disabled.

    const buttonUpList = $(".button-move-up");
    const buttonDownList = $(".button-move-down");
    console.log("call update_button_status")

    if (buttonUpList.length == 0) {
        console.log("no buttons found -> ending function")
        return;
    }

    // change button up list
    buttonUpList.prop("disabled", false);
    buttonUpList.first().prop("disabled", true);

    // change the button down list
    buttonDownList.prop("disabled", false);
    buttonDownList.last().prop("disabled", true);


}

$(document).ready(function () {

    console.log("test")
    $('.button-move-up, .button-move-down').on('click', function () {
        var $exercise = $(this).closest('.row');
        var currentPosition = $exercise.index();
        var newPosition = currentPosition;

        var trainingId = get_training_id();


        if ($(this).hasClass('button-move-up')) {
            newPosition -= 1;
        } else if ($(this).hasClass('button-move-down')) {
            newPosition += 1;
        }

        // Make AJAX request to update the order in the database
        $.ajax({
            url: `/api/actions/${trainingId}/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                action_type: 'reorder',
                position: currentPosition,
                arg: String(newPosition)
            }),
            success: function (response) {
                if (response.status === 'success') {
                    // Update the position data attribute
                    // $exercise.data('position', newPosition);
                    $exercise.slideUp(400, function () {
                        // Rearrange the elements on the page
                        if (newPosition < currentPosition) {
                            $exercise.insertBefore($exercise.prev())
                        } else {
                            {
                                $exercise.insertAfter($exercise.next())
                            }
                        }
                        $exercise.slideDown(400);
                        // Optionally, add some animation
                        // $exercise.css('font-weight', 'bold');
                        // setTimeout(function() {
                        //     $exercise.css('font-weight', 'inherit');
                        // }, 300);
                        update_button_status()
                    })
                }
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
                console.log(error.description)
            }

        })

    })
    update_button_status();
})