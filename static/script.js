// Wait until the HTML page has finished loading
document.addEventListener("DOMContentLoaded", () => {
  // Find all delete forms on the page
  const deleteForms = document.querySelectorAll(".delete-form");
  // Loop through each delete form
  deleteForms.forEach((form) => {
    // Run this check when the user clicks Delete
    form.addEventListener("submit", (event) => {
      // Read the student's name from data-student-name attribute
      const name = form.dataset.studentName || "this student";
      // Show browser confirm box; cancel form submit if user clicks Cancel
      if (!confirm(`Are you sure you want to delete ${name}?`)) {
        event.preventDefault(); // Stop the delete request
      }
    });
  });

  // Grab the search input, table, count label, and "no matches" message
  const searchInput = document.getElementById("searchInput");
  const studentsTable = document.getElementById("studentsTable");
  const studentCount = document.getElementById("studentCount");
  const noMatches = document.getElementById("noMatches");

  // Only run search code if both search box and table exist on this page
  if (searchInput && studentsTable) {
    // Get all table body rows as an array
    const rows = Array.from(studentsTable.querySelectorAll("tbody tr"));

    // Filter rows every time the user types in the search box
    searchInput.addEventListener("input", () => {
      const query = searchInput.value.trim().toLowerCase(); // Clean search text
      let visibleCount = 0; // Track how many rows match

      // Check each student row against the search query
      rows.forEach((row) => {
        const text = row.textContent.toLowerCase(); // All text in this row
        const matches = text.includes(query); // True if query appears in row
        row.style.display = matches ? "" : "none"; // Show match, hide non-match
        if (matches) visibleCount += 1; // Increase visible counter
      });

      // Update the displayed student count number
      if (studentCount) {
        studentCount.textContent = String(visibleCount);
      }
      // Show "No matching students found" if 0 rows match
      if (noMatches) {
        noMatches.style.display = visibleCount === 0 ? "block" : "none";
      }
    });
  }

  // Find every alert close ('x') button
  document.querySelectorAll(".alert-close").forEach((button) => {
    // Remove the alert box from the page when clicked
    button.addEventListener("click", () => {
      const alert = button.closest(".alert"); // Find parent alert div
      if (alert) alert.remove(); // Delete alert from DOM
    });
  });
});
