$(function () {
    console.log("hello world")

    let approachArea = $("#approach")
    let divApproachText = $("#approach-as-text")

    // start using a regular box

    divApproachText.click(function () {
        approachArea.css("display", "Block")
        divApproachText.css("display", "None")
        approachArea.focus()

    })

    approachArea.blur(function () {
        let approachHTML = approachArea.val().replace("\n", "<br>")
        console.log(approachHTML)
        approachArea.css("display", "None")
        divApproachText.css("display", "Block")
        divApproachText.empty().html("<p>" + approachHTML + "</p>")
    })


    approachArea.blur()
})