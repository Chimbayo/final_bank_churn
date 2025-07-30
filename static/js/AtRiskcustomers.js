document.addEventListener('DOMContentLoaded', function() {
    fetchWillLeaveCustomers();
    createTooltip();
});

// Mapping objects for human-readable values
const genderMap = { 0: "Female", 1: "Male" };
const regionMap = { 0: "Southern", 1: "Northern", 2: "Central" };
const customerTypeMap = { 0: "Retail", 1: "SME", 2: "Corporate" };
const employmentStatusMap = { 0: "Self Employed", 1: "Not Employed", 2: "Employed" };
const educationLevelMap = { 0: "Primary", 1: "Secondary", 2: "Tertiary" };
const netQualityMap = { 0: "Fair", 1: "Poor", 2: "Good" };
const phoneMap = { 0: "Yes", 1: "No" };
const mobileBankMap = { 0: "No", 1: "Yes" };
const locationTypeMap = { 0: "Rural", 1: "Urban", 2: "Semi Urban" };
const predictionMap = { 0: "Will Stay", 1: "Will Leave" };

const districtMap = {
    0: "Zomba", 1: "Thyolo", 2: "Chikwawa", 3: "Nkhata Bay", 4: "Machinga",
    5: "Karonga", 6: "Dedza", 7: "Chiradzulu", 8: "Mchinji", 9: "Ntchisi",
    10: "Kasungu", 11: "Chitipa", 12: "Nkhotakota", 13: "Neno", 14: "Mangochi",
    15: "Mulanje", 16: "Mzimba", 17: "Blantyre", 18: "Nsanje", 19: "Phalombe",
    20: "Likoma", 21: "Salima", 22: "Lilongwe", 23: "Mwanza", 24: "Rumphi",
    25: "Balaka", 26: "Dowa", 27: "Ntcheu", 28: "Unknown", 29: "Unknown"
};

// Create tooltip element
function createTooltip() {
    const tooltip = document.createElement('div');
    tooltip.id = 'customer-tooltip';
    tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 12px;
        border-radius: 8px;
        font-size: 14px;
        max-width: 300px;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        line-height: 1.4;
    `;
    document.body.appendChild(tooltip);
}

// Generate explanation for why customer might leave
function generateChurnExplanation(customer) {
    const reasons = [];
    const probability = (customer.churn_probability * 100).toFixed(1);
    
    // Balance-related factors
    if (customer.balance < 10000) {
        reasons.push("Low account balance");
    }
    
    // High outstanding loans
    if (customer.outstanding_loans > customer.balance * 2) {
        reasons.push("High debt-to-balance ratio");
    }
    
    // Low engagement
    if (customer.number_of_transactions_per_month < 5) {
        reasons.push("Low transaction activity");
    }
    
    // No mobile banking
    if (customer.mobile_banking_usage === 0) {
        reasons.push("Not using mobile banking");
    }
    
    // Complaints
    if (customer.num_of_complaints > 5) {
        reasons.push("Multiple service complaints");
    }
    
    // Distance to branch
    if (customer.proximity_to_nearestbranch_or_atm_km > 20) {
        reasons.push("Far from nearest branch/ATM");
    }
    
    // Income level
    if (customer.income_level < 50000) {
        reasons.push("Low income level");
    }
    
    // Build explanation message
    let explanation = `<strong>Churn Probability: ${probability}%</strong><br><br>`;
    
    if (reasons.length > 0) {
        explanation += "<strong>Key Risk Factors:</strong><br>";
        explanation += "• " + reasons.slice(0, 7).join("<br>• ");
        if (reasons.length > 7) {
            explanation += `<br>• ...and ${reasons.length - 4} more factors`;
        }
    } else {
        explanation += "Model prediction based on complex feature interactions.";
    }
    
    return explanation;
}

function fetchWillLeaveCustomers() {
    fetch('/api/customers/will_leave')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                displayError(data.error);
            } else {
                displayCustomers(data);
            }
        })
        .catch(error => {
            console.error('Error fetching customers:', error);
            displayError(error.message);
        });
}

function displayCustomers(customers) {
    const tableBody = document.querySelector('table tbody');
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    if (customers.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="24" style="text-align: center;">No customers at risk of leaving</td>';
        tableBody.appendChild(row);
        return;
    }
    
    customers.forEach(customer => {
        const row = document.createElement('tr');
        
        // Add class based on prediction
        if (customer.prediction === 1) {
            row.classList.add('churn');
        } else if (customer.prediction === 0) {
            row.classList.add('no-churn');
        }
        
        // Add tooltip functionality
        row.style.cursor = 'pointer';
        
        // Generate explanation for this customer
        const explanation = generateChurnExplanation(customer);
        
        // Add mouse events for tooltip
        row.addEventListener('mouseenter', function(e) {
            showTooltip(e, explanation);
        });
        
        row.addEventListener('mouseleave', function() {
            hideTooltip();
        });
        
        row.addEventListener('mousemove', function(e) {
            updateTooltipPosition(e);
        });
        
        // Map the customer data to table cells with human-readable values
        row.innerHTML = `
            <td>${customer.customer_id || ''}</td>
            <td>${customer.age || ''}</td>
            <td>${genderMap[customer.gender] ?? customer.gender}</td>
            <td>${districtMap[customer.district] ?? customer.district}</td>
            <td>${regionMap[customer.region] ?? customer.region}</td>
            <td>${locationTypeMap[customer.location_type] ?? customer.location_type}</td>
            <td>${customerTypeMap[customer.customer_type] ?? customer.customer_type}</td>
            <td>${employmentStatusMap[customer.employment_status] ?? customer.employment_status}</td>
            <td>${customer.income_level ? customer.income_level.toLocaleString() : ''}</td>
            <td>${educationLevelMap[customer.education_level] ?? customer.education_level}</td>
            <td>${customer.tenure || ''}</td>
            <td>${customer.balance ? customer.balance.toLocaleString() : ''}</td>
            <td>${customer.credit_score || ''}</td>
            <td>${customer.outstanding_loans ? customer.outstanding_loans.toLocaleString() : ''}</td>
            <td>${customer.num_of_products || ''}</td>
            <td>${mobileBankMap[customer.mobile_banking_usage] ?? (customer.mobile_banking_usage ? 'Yes' : 'No')}</td>
            <td>${customer.number_of_transactions_per_month || ''}</td>
            <td>${customer.num_of_complaints || ''}</td>
            <td>${customer.proximity_to_nearestbranch_or_atm_km || ''}</td>
            <td>${netQualityMap[customer.mobile_network_quality] ?? customer.mobile_network_quality}</td>
            <td>${phoneMap[customer.owns_mobile_phone] ?? (customer.owns_mobile_phone ? 'Yes' : 'No')}</td>
            <td>${predictionMap[customer.prediction] ?? customer.prediction}</td>
            <td>${customer.churn_probability ? (customer.churn_probability * 100).toFixed(2) + '%' : ''}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

function showTooltip(event, explanation) {
    const tooltip = document.getElementById('customer-tooltip');
    tooltip.innerHTML = explanation;
    tooltip.style.opacity = '1';
    updateTooltipPosition(event);
}

function hideTooltip() {
    const tooltip = document.getElementById('customer-tooltip');
    tooltip.style.opacity = '0';
}

function updateTooltipPosition(event) {
    const tooltip = document.getElementById('customer-tooltip');
    const tooltipRect = tooltip.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    let left = event.pageX + 15;
    let top = event.pageY - 10;
    
    // Adjust if tooltip would go off screen
    if (left + tooltipRect.width > viewportWidth) {
        left = event.pageX - tooltipRect.width - 15;
    }
    
    if (top + tooltipRect.height > viewportHeight) {
        top = event.pageY - tooltipRect.height - 10;
    }
    
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
}

function displayError(errorMessage) {
    const tableBody = document.querySelector('table tbody');
    tableBody.innerHTML = `
        <tr>
            <td colspan="24" style="text-align: center; color: red;">
                Error loading data: ${errorMessage}
            </td>
        </tr>
    `;
}