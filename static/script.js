function addStudent() {
    let name = document.getElementById("name").value;
    let roll = document.getElementById("roll").value;
    let dept = document.getElementById("dept").value;

    if (name === "" || roll === "" || dept === "") {
        alert("Please fill all fields.");
        return;
    }

    let list = document.getElementById("studentList");

    let item = document.createElement("li");
    item.textContent =
        "Name: " + name +
        " | Roll No: " + roll +
        " | Department: " + dept;

    list.appendChild(item);

    // Clear input fields
    document.getElementById("name").value = "";
    document.getElementById("roll").value = "";
    document.getElementById("dept").value = "";
}

function clearStudents() {
    document.getElementById("studentList").innerHTML = "";
}

function searchStudent() {
    let search = document.getElementById("searchBox").value.toLowerCase();
    let students = document.getElementById("studentList").getElementsByTagName("li");

    for (let i = 0; i < students.length; i++) {
        let text = students[i].textContent.toLowerCase();

        if (text.includes(search)) {
            students[i].style.display = "";
        } else {
            students[i].style.display = "none";
        }
    }
}