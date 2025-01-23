// js for the edit-exercise endpoint

const fileTypes = [
  "image/apng",
  "image/bmp",
  "image/gif",
  "image/jpeg",
  "image/pjpeg",
  "image/png",
  "image/svg+xml",
  "image/tiff",
  "image/webp",
  "image/x-icon",
];

const deleteButtons = $(".button-delete")

function validFileType(file) {
  return fileTypes.includes(file.type);
}

function returnFileSize(number) {
  if (number < 1e3) {
    return `${number} bytes`;
  } else if (number >= 1e3 && number < 1e6) {
    return `${(number / 1e3).toFixed(1)} KB`;
  } else {
    return `${(number / 1e6).toFixed(1)} MB`;
  }
}
function updateImageDisplay() {
  // updates the image preview display based on the images selected in the #new_inputs file input
  const preview = $(".preview");
  const input = $("#new_images_field");
  preview.empty()


  const curFiles = input.length ? input[0].files : [];
  if (curFiles.length === 0) {
    const para = $("<p>");
    para.text("No files currently selected for upload");
    preview.append(para);
  } else {

    for (const file of curFiles) {
      if (validFileType(file)) {
        preview.append($(
            `<div class="col col-3"><img src="${URL.createObjectURL(file)}" class="img-thumbnail">
              <p>File name ${file.name}, file size ${returnFileSize(file.size)}.</p>
              </div>`))
      } else {
        preview.append($(`<div class="col col-3"><p>File name ${file.name}: Not a valid file type. Update your selection.</p>`))
      }
    }
  }
}

function toggleImageWithDelete(deleteButton) {
    const deleteButtonJQ = $(deleteButton)
    const imgDiv = deleteButtonJQ.parent().parent();
    const buttonIsActive = deleteButtonJQ.prop("checked");
    console.log("button " + deleteButton.id + " is active: " + buttonIsActive);
    buttonIsActive ? imgDiv.addClass("image-delete") : imgDiv.removeClass("image-delete");
}


function resetDeleteButtons() {
  // resets the delete buttons and their images
  deleteButtons.prop("checked", false);
  deleteButtons.each(function(index, element) {
    toggleImageWithDelete(element)
      }
  )
}

$(function () {


  // style the elements for deleting existing images
  let thumpnailImages = $("img").css({"cursor": "pointer"})
  let myModal = new bootstrap.Modal(document.getElementById('modal'), {})

  thumpnailImages.click( function() {
    // adds responsiveness to images to show in lightbox
    let imageSrc = $(this).attr("src");
    $("#modal-target").attr("src", imageSrc);
    myModal.show()

  })

  // create gray out effect for images selected for deletion via the delete button
  deleteButtons.click( function(event) {
    toggleImageWithDelete(event.currentTarget);
  })

  // ensure that reset also resets the delete buttons and the image display
  $("#form-reset").click(function () {
    $("form")[0].reset()

    updateImageDisplay();
    resetDeleteButtons();
  })
  $("#new_images_field").change(updateImageDisplay)
})