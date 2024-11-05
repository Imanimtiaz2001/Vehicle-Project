document.addEventListener('DOMContentLoaded', function () {
    // Handle form submission
    $('#searchForm').on('submit', function (e) {
        e.preventDefault(); // Prevent the default form submission

        const year = $('#year').val();
        const make = $('#make').val();
        const model = $('#model').val();
        const mileage = $('#mileage').val();

        // Send request to backend API
        $.ajax({
            url: 'http://localhost:5000/',  // Ensure this URL matches your backend endpoint
            method: 'GET',
            data: {
                year: year,
                make: make,
                model: model,
                mileage: mileage
            },
            success: function (response) {
                // Store the response data in localStorage
                window.localStorage.setItem('searchResults', JSON.stringify(response));
                // Redirect to results page
                window.location.href = 'results.html';
            },
            error: function (error) {
                console.error('Error fetching data:', error);
                alert('Error fetching data from the server. Please try again.');
            }
        });
    });

    // Load and display search results
    if (window.location.pathname.endsWith('results.html')) {
        const response = JSON.parse(window.localStorage.getItem('searchResults'));

        // Ensure response data is available before populating results
        if (response) {
            // Set estimated price
            $('#estimatedPrice').text(`Estimated Market Value: ${response.estimated_market_value}`);

            // Populate results table
            const resultsTableBody = $('#resultsTableBody');
            resultsTableBody.empty(); // Clear any existing rows
            response.listings.slice(0, 100).forEach((listing) => {
                resultsTableBody.append(`
                    <tr>
                        <td>${listing.year} ${listing.make} ${listing.model} ${listing.trim}</td>
                        <td>${listing.listing_price}</td>
                        <td>${listing.listing_mileage}</td>
                        <td>${listing.location}</td>
                    </tr>
                `);
            });
        } else {
            $('#estimatedPrice').text('No results found.');
        }
    }
});
