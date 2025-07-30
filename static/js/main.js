
document.addEventListener('DOMContentLoaded', function () {
    const lowRiskBtn = document.getElementById('low-risk-btn');
    const mediumRiskBtn = document.getElementById('medium-risk-btn');
    const highRiskBtn = document.getElementById('high-risk-btn');
    const exportBtn = document.getElementById("export-btn");
    const resultsBody = document.getElementById("results-body");

    // Lookup tables for human-friendly labels
    const genderMap = { 0: "Female", 1: "Male" };
    const regionMap = { 0: "Southern", 1: "Northern", 2: "Central" };
    const customerTypeMap = { 0: "Retail", 1: "SME", 2: "Corporate" };
    const employmentStatusMap = { 0: "Self Employed", 1: "Not Employed", 2: "Employed" };
    const educationLevelMap = { 0: "Primary", 1: "Secondary", 2: "Tertiary" };
    const netQualityMap = { 0: "Fair", 1: "Poor", 2: "Good" };
    const phoneMap = { 0: "Yes", 1: "No" };
    const mobileBankMap = { 0: "No", 1: "Yes" };
    const locationTypeMap = { 0: "Rural", 1: "Urban", 2: "Semi Urban" };

    const districtMap = {
        0: "Zomba", 1: "Thyolo", 2: "Chikwawa", 3: "Nkhata Bay", 4: "Machinga",
        5: "Karonga", 6: "Dedza", 7: "Chiradzulu", 8: "Mchinji", 9: "Ntchisi",
        10: "Kasungu", 11: "Chitipa", 12: "Nkhotakota", 13: "Neno", 14: "Mangochi",
        15: "Mulanje", 16: "Mzimba", 17: "Blantyre", 18: "Nsanje", 19: "Phalombe",
        20: "Likoma", 21: "Salima", 22: "Lilongwe", 23: "Mwanza", 24: "Rumphi",
        25: "Balaka", 26: "Dowa", 27: "Ntcheu", 28: "Unknown", 29: "Unknown"
    };

    let currentRiskLevel = 'low'; // default to low risk
    let currentMinThreshold = 0;
    let currentMaxThreshold = 35;
    // Add active indicator style to CSS (add this to your stylesheet)
    const style = document.createElement('style');
    style.textContent = `
        .risk-btn.active {
            position: relative;
            font-weight: bold;
        }
        .risk-btn.active::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 100%;
            height: 3px;
            background-color: #3b82f6;
            border-radius: 3px;
        }
        #low-risk-btn.active::after { background-color: #10b981; }
        #medium-risk-btn.active::after { background-color: #f59e0b; }
        #high-risk-btn.active::after { background-color: #ef4444; }
    `;
    document.head.appendChild(style);


    // Set up event listeners for risk buttons
    lowRiskBtn.addEventListener('click', function() {
        setActiveButton('low');
        currentMinThreshold = 0;
        currentMaxThreshold = 35.999;
        loadCustomers(currentMinThreshold, currentMaxThreshold);
    });

    mediumRiskBtn.addEventListener('click', function() {
        setActiveButton('medium');
        currentMinThreshold = 36;
        currentMaxThreshold = 69.999;
        loadCustomers(currentMinThreshold, currentMaxThreshold);
    });

    highRiskBtn.addEventListener('click', function() {
        setActiveButton('high');
        currentMinThreshold = 70;
        currentMaxThreshold = 100;
        loadCustomers(currentMinThreshold, currentMaxThreshold);
    });

    function setActiveButton(level) {
        currentRiskLevel = level;
        lowRiskBtn.classList.remove('active');
        mediumRiskBtn.classList.remove('active');
        highRiskBtn.classList.remove('active');
        
        if (level === 'low') lowRiskBtn.classList.add('active');
        if (level === 'medium') mediumRiskBtn.classList.add('active');
        if (level === 'high') highRiskBtn.classList.add('active');
    }

    function loadCustomers(minThreshold, maxThreshold) {
        fetch(`/api/customers/predicted?min=${minThreshold}&max=${maxThreshold}`)
            .then(response => response.json())
            .then(data => {
                resultsBody.innerHTML = "";

                const riskLevelText = currentRiskLevel === 'low' ? 'Low Risk' : 
                                   currentRiskLevel === 'medium' ? 'Medium Risk' : 
                                   'High Risk';
                
                document.querySelector('h2').textContent = `Customers at ${riskLevelText} are : ${data.length}`;

                if (data.length === 0) {
                    resultsBody.innerHTML = `
                        <tr>
                            <td colspan="23" style="text-align:center; color: #666; padding: 40px; font-style: italic;">
                                No customers found in this risk category.
                            </td>
                        </tr>`;
                    return;
                }

                for (const customer of data) {
                    const row = document.createElement("tr");
                    const probability = parseFloat(customer.churn_probability) * 100;
                    const isHighRisk = probability >= 50;
                    
                    row.className = isHighRisk ? "high-risk-row" : "low-risk-row";

                    row.innerHTML = `
                        <td class="p-3">${customer.customer_id ?? ""}</td>
                        <td class="p-3">${customer.age ?? ""}</td>
                        <td class="p-3">${genderMap[customer.gender] ?? customer.gender}</td>
                        <td class="p-3">${districtMap[customer.district] ?? customer.district}</td>
                        <td class="p-3">${regionMap[customer.region] ?? customer.region}</td>
                        <td class="p-3">${locationTypeMap[customer.location_type] ?? customer.location_type}</td>
                        <td class="p-3">${customerTypeMap[customer.customer_type] ?? customer.customer_type}</td>
                        <td class="p-3">${employmentStatusMap[customer.employment_status] ?? customer.employment_status}</td>
                        <td class="p-3">${customer.income_level ?? ""}</td>
                        <td class="p-3">${educationLevelMap[customer.education_level] ?? customer.education_level}</td>
                        <td class="p-3">${customer.tenure ?? ""}</td>
                        <td class="p-3">${customer.balance ?? ""}</td>
                        <td class="p-3">${customer.credit_score ?? ""}</td>
                        <td class="p-3">${customer.outstanding_loans ?? ""}</td>
                        <td class="p-3">${customer.num_of_products ?? ""}</td>
                        <td class="p-3">${mobileBankMap[customer.mobile_banking_usage] ?? customer.mobile_banking_usage}</td>
                        <td class="p-3">${customer.number_of_transactions_per_month ?? ""}</td>
                        <td class="p-3">${customer.num_of_complaints ?? ""}</td>
                        <td class="p-3">${customer.proximity_to_nearestbranch_or_atm_km ? parseFloat(customer.proximity_to_nearestbranch_or_atm_km).toFixed(1) + ' km' : ""}</td>
                        <td class="p-3">${netQualityMap[customer.mobile_network_quality] ?? customer.mobile_network_quality}</td>
                        <td class="p-3">${phoneMap[customer.owns_mobile_phone] ?? customer.owns_mobile_phone}</td>
                        <td class="p-3">${
                            customer.prediction === 1
                                ? '<span class="prediction-churn">Will Leave</span>'
                                : customer.prediction === 0
                                    ? '<span class="prediction-stay">Will Stay</span>'
                                    : ''
                        }</td>
                        <td class="p-3">${
                            customer.churn_probability !== null && customer.churn_probability !== undefined
                                ? `<span class="${isHighRisk ? 'probability-high' : 'probability-low'}">${probability.toFixed(1)}%</span>`
                                : ""
                        }</td>
                    `;
                    resultsBody.appendChild(row);
                }

                addZebraStriping();
            })
            .catch(error => {
                console.error("Error fetching customers:", error);
                resultsBody.innerHTML = `
                    <tr>
                        <td colspan="23" style="text-align:center; color: #ef4444; padding: 40px;">
                            Error loading customer data. Please try again.
                        </td>
                    </tr>`;
            });
    }

    function addZebraStriping() {
        const rows = resultsBody.querySelectorAll('tr');
        rows.forEach((row, index) => {
            row.classList.remove('zebra-even', 'zebra-odd');
            if (index % 2 === 0) {
                row.classList.add('zebra-even');
            } else {
                row.classList.add('zebra-odd');
            }
        });
    }

    // Auto-refresh every 5 seconds
    setInterval(() => {
        loadCustomers(currentMinThreshold, currentMaxThreshold);
    }, 5000);

    exportBtn.addEventListener("click", () => {
                const riskLevelText = currentRiskLevel === 'low' ? 'low_risk_0_35' : 
                                    currentRiskLevel === 'medium' ? 'medium_risk_36_69' : 
                                    'high_risk_70_100';
                
                // Initialize CSV content
                let csvContent = "";
                
                // Add headers
                const headers = [];
                document.querySelectorAll("#results-table thead th").forEach(th => {
                    headers.push(`"${th.textContent.trim()}"`);
                });
                csvContent += headers.join(",") + "\n";

                // Add rows
                const rows = [];
                resultsBody.querySelectorAll("tr").forEach(tr => {
                    const cells = [];
                    tr.querySelectorAll("td").forEach(td => {
                        let text = td.textContent.trim();
                        // Handle special cases for formatted content
                        if (td.querySelector('.prediction-churn, .prediction-stay, .probability-high, .probability-low')) {
                            text = td.textContent.trim();
                        }
                        text = text.replace(/"/g, '""');
                        cells.push(`"${text}"`);
                    });
                    rows.push(cells.join(","));
                });

                if (rows.length === 0) {
                    alert("No data to export.");
                    return;
                }

                csvContent += rows.join("\n");

                // Create and trigger download
                const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.setAttribute("href", url);
                link.setAttribute("download", `customers_${riskLevelText}_${new Date().toISOString().slice(0,10)}.csv`);
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                setTimeout(() => {
                    URL.revokeObjectURL(url);
                }, 100);
            });

    // Initial load
    setActiveButton('low');
    loadCustomers(0, 35);
});
// This script handles the total customers count on the main page
// It fetches the total number of customers from the API and updates the display
document.addEventListener("DOMContentLoaded", () => {

    function refreshTotalCustomers() {
        fetch("/api/customers")
            .then(response => response.json())
            .then(data => {
                document.getElementById("total-customers").textContent = data.total;
            })
            .catch(err => {
                console.error(err);
                document.getElementById("total-customers").textContent = "Error loading";
            });
    }

    // Load initially
    refreshTotalCustomers();

    // Refresh every 10 seconds
    setInterval(refreshTotalCustomers, 5000);
});

// This script handles the churn rate display on the main page
// It fetches the churn rate from the API and updates the display
document.addEventListener("DOMContentLoaded", () => {
    function loadChurnRate() {
        fetch("/api/customers/churn_rate")
            .then(response => response.json())
            .then(data => {
                document.getElementById("churn_rate").textContent = data.churn_rate + "%";
            })
            .catch(err => {
                console.error(err);
                document.getElementById("churn_rate").textContent = "Error";
            });
    }

    // load immediately
    loadChurnRate();

    // refresh every 10 seconds (optional)
    setInterval(loadChurnRate, 10000);
});




