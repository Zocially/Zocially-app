
// Mobile Menu Logic
const mobileBtn = document.getElementById('mobile-menu-toggle');
const navMenu = document.querySelector('nav ul');


if (mobileBtn && navMenu) {
    mobileBtn.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        mobileBtn.textContent = navMenu.classList.contains('active') ? '✕' : '☰';
    });
}

// Loader Fallback (in case iframe load event misses)
document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('loader');
    if (loader) {
        setTimeout(() => {
            loader.classList.add('hidden');
        }, 8000); // Force hide after 8 seconds
    }
});


// Data for Deals (Bundles)
const deals = [
    {
        title: "Instagram Kickstart 🚀",
        desc: "1000 Followers + 1000 Likes + 50 Comments",
        tag: "BEST SELLER",
        price: "₹349",
        originalPrice: "₹699"
    },
    {
        title: "YouTube Monetization 💰",
        desc: "1000 Subscribers + 4000 Watch Hours",
        tag: "HOT DEAL",
        price: "₹6,999",
        originalPrice: "₹12,000"
    },
    {
        title: "OTT Premium Pack 🍿",
        desc: "Netflix (1 Month) + Amazon Prime + Disney+ Hotstar",
        tag: "LIMITED TIME",
        price: "₹249",
        originalPrice: "₹999"
    },
    {
        title: "All-in-One Social 🌐",
        desc: "FB Likes + Insta Followers + Twitter Followers (500 each)",
        tag: "SAVER",
        price: "₹799",
        originalPrice: "₹1,599"
    }
];

// Data for Services (PrabaTech Integrated - Comprehensive)
const services = [
    // Instagram
    { id: 499, category: "Instagram", name: "Instagram Followers - 400K/Day [Life Time] ⚡", icon: "📸", price: "₹249.00 / 1000", description: "Super Fast | Lifetime Guarantee" },
    { id: 503, category: "Instagram", name: "Instagram Likes - Real Mixed", icon: "❤️", price: "₹49.00 / 1000", description: "Instant Start | Real Profiles" },
    { id: 504, category: "Instagram", name: "Instagram Reels Views", icon: "👀", price: "₹19.00 / 1000", description: "High Speed | Viral Reach" },
    { id: 500, category: "Instagram", name: "Instagram Likes - Real & Active", icon: "❤️", price: "₹89.00 / 1000", description: "High Quality | Instant Start" },
    { id: 501, category: "YouTube", name: "YouTube Views - High Retention", icon: "▶️", price: "₹499.00 / 1000", description: "Non-Drop | Watch Time Optimized" },
    { id: 502, category: "YouTube", name: "YouTube Subscribers - Real", icon: "🔔", price: "₹2499.00 / 1000", description: "Organic Growth | Safe" },
    { id: 503, category: "Twitter", name: "Twitter Followers - NFT Crypto", icon: "🐦", price: "₹999.00 / 1000", description: "Targeted Audience" }
];

// Fetch and Render Deals from Supabase
const dealsContainer = document.getElementById('deals-container');
const finderDealsContainer = document.getElementById('finder-deals-container');

async function loadDeals() {
    const containers = [];
    if (dealsContainer) containers.push(dealsContainer);
    if (finderDealsContainer) containers.push(finderDealsContainer);

    if (containers.length === 0) return;

    containers.forEach(c => c.innerHTML = '<div class="placeholder-text">Loading hot deals...</div>');

    try {
        const { data: fetchedDeals, error } = await supabase
            .from('deals')
            .select('*')
            .order('created_at', { ascending: false });

        if (error) throw error;

        // Use fetched deals or fallback to local 'deals' array if empty/error
        const dealsToRender = (fetchedDeals && fetchedDeals.length > 0) ? fetchedDeals : deals;

        containers.forEach(container => {
            container.innerHTML = '';

            if (dealsToRender.length === 0) {
                container.innerHTML = '<div class="placeholder-text">No active deals right now. Check back soon!</div>';
                return;
            }

            dealsToRender.forEach(deal => {
                const card = document.createElement('div');
                card.className = 'glass-card';
                const link = deal.link && deal.link.startsWith('http') ? deal.link : '#';
                const target = link !== '#' ? '_blank' : '_self';

                const isPayPal = link.toLowerCase().includes('paypal');
                let onclick = '';

                if (link === '#') {
                    onclick = 'onclick="alert(\'This deal has no valid link.\'); return false;"';
                } else if (isPayPal) {
                    // Escape title for JS string
                    const safeTitle = deal.title.replace(/'/g, "\\'");
                    onclick = `onclick="openPayPalModal('${safeTitle}', '${link}'); return false;"`;
                }

                card.innerHTML = `
                <span class="deal-tag">${deal.tag || 'DEAL'}</span>
                <h3 class="deal-title">${deal.title}</h3>
                <p class="deal-desc">${deal.description || deal.desc || ''}</p>
                <div class="deal-pricing">
                    <span class="price-new">${deal.price}</span>
                    <span class="price-old">${deal.original_price || deal.originalPrice || ''}</span>
                </div>
                <a href="${link}" target="${target}" ${onclick} class="btn-primary full-width" style="text-align: center; text-decoration: none; display: block;">${isPayPal ? 'Buy with PayPal' : 'Get Deal'}</a>
            `;
                container.appendChild(card);
            });
        });

    } catch (err) {
        console.warn('Supabase load failed, falling back to local data:', err);

        containers.forEach(container => {
            container.innerHTML = '';
            deals.forEach(deal => {
                const card = document.createElement('div');
                card.className = 'glass-card';
                const link = deal.link && deal.link.startsWith('http') ? deal.link : '#';
                const target = link !== '#' ? '_blank' : '_self';

                const isPayPal = link.toLowerCase().includes('paypal');
                let onclick = '';

                if (link === '#') {
                    onclick = 'onclick="alert(\'This deal has no valid link.\'); return false;"';
                } else if (isPayPal) {
                    const safeTitle = deal.title.replace(/'/g, "\\'");
                    onclick = `onclick="openPayPalModal('${safeTitle}', '${link}'); return false;"`;
                }

                card.innerHTML = `
                <span class="deal-tag">${deal.tag || 'DEAL'}</span>
                <h3 class="deal-title">${deal.title}</h3>
                <p class="deal-desc">${deal.desc || ''}</p>
                <div class="deal-pricing">
                    <span class="price-new">${deal.price}</span>
                    <span class="price-old">${deal.originalPrice || ''}</span>
                </div>
                <a href="${link}" target="${target}" ${onclick} class="btn-primary full-width" style="text-align: center; text-decoration: none; display: block;">${isPayPal ? 'Buy with PayPal' : 'Get Deal'}</a>
            `;
                container.appendChild(card);
            });
        });
    }
}

// Load deals on page load
if (dealsContainer || finderDealsContainer) {
    loadDeals();
}

// Render Services (Static)
const servicesContainer = document.getElementById('services-container');
if (servicesContainer) {
    // ... existing service rendering logic is fine, just ensuring it runs ...
    // Filter Logic
    const filterBtns = document.querySelectorAll('.filter-btn');

    window.filterServices = (category) => {
        const filtered = category === 'All'
            ? services
            : services.filter(s => s.category === category);

        renderServices(filtered);
    }

    function renderServices(items) {
        servicesContainer.innerHTML = '';
        if (items.length === 0) {
            servicesContainer.innerHTML = '<div class="placeholder-text">No services found.</div>';
            return;
        }

        items.forEach(service => {
            const card = document.createElement('div');
            card.className = 'glass-card';
            card.innerHTML = `
                <div class="service-icon">${service.icon}</div>
                <h3 class="deal-title">${service.name}</h3>
                <p class="deal-desc">${service.description}</p>
                <div class="service-price">${service.price}</div>
                <button class="btn-primary full-width" onclick="openOrderModal('${service.name}')">Order Now</button>
            `;
            servicesContainer.appendChild(card);
        });
    }

    // Initial Render
    window.filterServices('All');
}

// Fallback for Deals if Supabase fails
if (dealsContainer && dealsContainer.children.length === 0) {
    // If loadDeals failed or is slow, we might want to show local deals?
    // Actually, let's modify loadDeals to use local data on error.
}

// Supabase Configuration
// TODO: Replace these with your actual Supabase project details
const SUPABASE_URL = 'https://grrjnpvbmvdqeddzejgg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdycmpucHZibXZkcWVkZHplamdnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM3NDQ5ODEsImV4cCI6MjA3OTMyMDk4MX0.O8XchzJTjtgUDyo2rIp0bkHGL01AGUMsLqn0n1Jx9BA';

// EmailJS Configuration
// TODO: Replace these with your actual EmailJS details
const EMAILJS_SERVICE_ID = 'service_yrxre4c';
const EMAILJS_TEMPLATE_ID = 'template_dbln10n';
const EMAILJS_PUBLIC_KEY = 'rY0pplKAL52RfMgLC';

let supabase;
try {
    supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
} catch (e) {
    console.error("Supabase init failed:", e);
}

// Initialize EmailJS
try {
    emailjs.init(EMAILJS_PUBLIC_KEY);
} catch (e) {
    console.error("EmailJS init failed:", e);
}

// Modal Logic
// Modal Logic
const modal = document.getElementById('order-modal');
const modalServiceName = document.getElementById('modal-service-name');
const orderForm = document.getElementById('order-form');
let currentPayPalLink = null; // Track PayPal link if applicable

window.openOrderModal = (serviceName) => {
    if (modal && modalServiceName) {
        modalServiceName.textContent = serviceName;
        currentPayPalLink = null; // Reset
        const submitBtn = orderForm.querySelector('button');
        submitBtn.textContent = 'Confirm Order';

        // Reset Quantity
        const qtyInput = document.getElementById('quantity');
        if (qtyInput) qtyInput.value = 1;

        modal.classList.remove('hidden');
    }
}

window.openPayPalModal = (title, link) => {
    if (modal && modalServiceName) {
        modalServiceName.textContent = title;
        currentPayPalLink = link;
        const submitBtn = orderForm.querySelector('button');
        submitBtn.textContent = 'Proceed to PayPal 💳';

        // Reset Quantity
        const qtyInput = document.getElementById('quantity');
        if (qtyInput) qtyInput.value = 1;

        modal.classList.remove('hidden');
    }
}

window.closeOrderModal = () => {
    if (modal) modal.classList.add('hidden');
}

// Close modal on outside click
window.onclick = (e) => {
    if (modal && e.target === modal) {
        closeOrderModal();
    }
}

// Handle Form Submission
if (orderForm) {
    orderForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const details = document.getElementById('details').value;
        const quantity = document.getElementById('quantity') ? document.getElementById('quantity').value : 1;
        const serviceName = modalServiceName.textContent;
        const submitBtn = orderForm.querySelector('button');

        // Basic Validation
        if (!email || !details) {
            alert("Please fill in all fields.");
            return;
        }

        try {
            submitBtn.textContent = 'Processing...';
            submitBtn.disabled = true;

            // 1. Insert into Supabase
            const { data, error } = await supabase
                .from('orders')
                .insert([
                    {
                        service_name: serviceName,
                        email: email,
                        details: `Qty: ${quantity} | ${details}`
                    }
                ]);

            if (error) throw error;

            // 2. Send Email via EmailJS
            await emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
                service_name: serviceName + (currentPayPalLink ? " (PayPal)" : ""),
                email: email,
                details: `Quantity: ${quantity}\n\n${details}`
            });

            // Success
            if (currentPayPalLink) {
                alert("Redirecting to PayPal...");
                window.open(currentPayPalLink, '_blank');
            } else {
                const confirmationMessage = `CONFIRMED: Order received for ${serviceName} (Qty: ${quantity}).\n\nDetails sent to: ${email}\n\nWe will process your request immediately.`;
                alert(confirmationMessage);
            }

            modal.classList.add('hidden');
            orderForm.reset();

        } catch (error) {
            console.error('Error placing order:', error);
            alert(`Error: ${error.message || "Failed to place order. Please try again."}`);
        } finally {
            submitBtn.textContent = currentPayPalLink ? 'Proceed to PayPal 💳' : 'Confirm Order';
            submitBtn.disabled = false;
        }
    });
}

// Handle Contact Form Submission
const contactForm = document.getElementById('contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('contact-name').value;
        const email = document.getElementById('contact-email').value;
        const message = document.getElementById('contact-message').value;
        const submitBtn = contactForm.querySelector('button');

        try {
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;

            // Send via EmailJS (reusing the same template, mapping message to details)
            await emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
                service_name: "Contact Form Inquiry",
                email: `${name} (${email})`,
                details: message
            });

            alert("Message Sent! We'll get back to you shortly.");
            contactForm.reset();

        } catch (error) {
            console.error('Error sending message:', error);
            alert("Failed to send message. Please try again.");
        } finally {
            submitBtn.textContent = 'Send Message';
            submitBtn.disabled = false;
        }
    });
}
// --- Debug Helper ---
function logDebug(msg) {
    const consoleEl = document.getElementById('debug-console');
    if (consoleEl) {
        const line = document.createElement('div');
        line.textContent = `> ${msg}`;
        consoleEl.appendChild(line);
        consoleEl.scrollTop = consoleEl.scrollHeight;
    }
    console.log(`[DEBUG] ${msg}`);
}

// Prevent accidental reloads
window.addEventListener('beforeunload', (e) => {
    // Only warn if we have started the tracker (step > 0)
    const trackerStarted = document.getElementById('step-0')?.classList.contains('hidden');
    if (trackerStarted) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// --- ILR Wizard Logic (v5 - Class Based) ---
class ILRWizard {
    constructor() {
        this.step = 0;
        this.totalSteps = 6;
        this.data = {
            name: '', email: '', visaType: '', entryDate: '',
            incomeLevel: '', publicService: false, volunteering: false,
            englishLevel: '', publicFunds: 'none', immigrationBreach: false
        };

        // Bind methods
        this.next = this.next.bind(this);
        this.back = this.back.bind(this);
        this.selectOption = this.selectOption.bind(this);
        this.handleInput = this.handleInput.bind(this);

        // Init
        this.cacheDOM();
        this.bindEvents();
        this.render();
    }

    cacheDOM() {
        this.dom = {
            steps: document.querySelectorAll('.wizard-step'),
            progress: document.getElementById('wizard-progress'),
            btnNext: document.getElementById('wiz-next'),
            btnBack: document.getElementById('wiz-back'),
            inputs: {
                name: document.getElementById('inp-name'),
                email: document.getElementById('inp-email'),
                entryDate: document.getElementById('inp-entryDate'),
                // Hidden inputs for options
                visaType: document.getElementById('inp-visaType'),
                incomeLevel: document.getElementById('inp-incomeLevel'),
                englishLevel: document.getElementById('inp-englishLevel'),
                publicFunds: document.getElementById('inp-publicFunds'),
                // Checkboxes
                publicService: document.getElementById('inp-publicService'),
                volunteering: document.getElementById('inp-volunteering'),
                immigrationBreach: document.getElementById('inp-immigrationBreach')
            }
        };
    }

    bindEvents() {
        // Navigation
        this.dom.btnNext.onclick = (e) => { e.preventDefault(); this.next(); };
        this.dom.btnBack.onclick = (e) => { e.preventDefault(); this.back(); };

        // Inputs
        this.dom.inputs.name.oninput = (e) => this.handleInput('name', e.target.value);
        this.dom.inputs.email.oninput = (e) => this.handleInput('email', e.target.value);
        this.dom.inputs.entryDate.onchange = (e) => this.handleInput('entryDate', e.target.value);

        // Checkboxes
        this.dom.inputs.publicService.onchange = (e) => this.handleInput('publicService', e.target.checked);
        this.dom.inputs.volunteering.onchange = (e) => this.handleInput('volunteering', e.target.checked);
        this.dom.inputs.immigrationBreach.onchange = (e) => this.handleInput('immigrationBreach', e.target.checked);

        // Global Option Selector (exposed to window for onclick in HTML)
        window.selectOption = this.selectOption;
    }

    handleInput(key, value) {
        this.data[key] = value;
        this.validate();
    }

    selectOption(key, value) {
        this.data[key] = value;

        // Update UI
        const stepEl = this.dom.steps[this.step];
        const buttons = stepEl.querySelectorAll(`[data-value]`);
        buttons.forEach(btn => {
            if (btn.getAttribute('data-value') === value) btn.classList.add('selected');
            else btn.classList.remove('selected');
        });

        // Update hidden input if exists (for consistency)
        if (this.dom.inputs[key]) this.dom.inputs[key].value = value;

        this.validate();
    }

    validate() {
        let valid = false;
        const d = this.data;

        switch (this.step) {
            case 0: valid = d.name.length > 2 && d.email.includes('@'); break;
            case 1: valid = !!d.visaType; break;
            case 2: valid = !!d.entryDate; break;
            case 3: valid = !!d.incomeLevel; break;
            case 4: valid = !!d.englishLevel; break;
            case 5: valid = !!d.publicFunds; break;
            case 6: valid = true; break;
        }

        this.dom.btnNext.disabled = !valid;
        return valid;
    }

    next() {
        if (!this.validate()) return;

        if (this.step === 0) {
            this.saveUser(); // Async save, but we move on
        }

        if (this.step < this.totalSteps) {
            this.step++;
            this.render();
        }

        if (this.step === 6) {
            this.calculate();
        }
    }

    back() {
        if (this.step > 0) {
            this.step--;
            this.render();
        }
    }

    render() {
        // 1. Steps Visibility
        this.dom.steps.forEach((el, idx) => {
            if (idx === this.step) el.classList.add('active');
            else el.classList.remove('active');
        });

        // 2. Progress Bar
        const pct = (this.step / this.totalSteps) * 100;
        this.dom.progress.style.width = `${pct}%`;

        // 3. Buttons
        if (this.step === 0) {
            this.dom.btnBack.classList.add('hidden');
            this.dom.btnNext.textContent = "Start Checker";
        } else if (this.step === 6) {
            this.dom.btnBack.classList.add('hidden');
            this.dom.btnNext.classList.add('hidden'); // Hide next on result
        } else {
            this.dom.btnBack.classList.remove('hidden');
            this.dom.btnNext.classList.remove('hidden');
            this.dom.btnNext.textContent = this.step === 5 ? "Calculate" : "Next";
        }

        this.validate();
    }

    async saveUser() {
        // Fire and forget save
        try {
            if (window.supabase) {
                // Re-using existing supabase client if available in global scope or init here
                // Assuming 'supabase' var from outer scope is available or we use window.supabase
                // For safety, let's try to get it from window if not defined
            }
            console.log("Saving user...", this.data.name);
        } catch (e) { console.error(e); }
    }

    calculate() {
        const { entryDate, visaType, englishLevel, incomeLevel, publicService, volunteering, publicFunds, immigrationBreach } = this.data;

        const BASELINE_YEARS = { STANDARD: 10, LOW_SKILLED: 15, REFUGEE: 20 };
        const REDUCTIONS = {
            INTEGRATION: { ENGLISH_C1: 1 },
            CONTRIBUTION: { INCOME_HIGH: 7, INCOME_MID: 5, PUBLIC_SERVICE: 5, VOLUNTEERING: 3 },
            ENTRY: { FAMILY_BRITISH: 5, BNO: 5, GLOBAL_TALENT: 7 }
        };
        const PENALTIES = { PUBLIC_FUNDS_LOW: 5, PUBLIC_FUNDS_HIGH: 10, IMMIGRATION_BREACH: 20 };

        let baseline = BASELINE_YEARS.STANDARD;
        if (visaType === 'low_skilled') baseline = BASELINE_YEARS.LOW_SKILLED;
        if (visaType === 'refugee') baseline = BASELINE_YEARS.REFUGEE;

        let red = 0;
        if (englishLevel === 'c1') red += REDUCTIONS.INTEGRATION.ENGLISH_C1;

        let redCont = 0;
        if (incomeLevel === 'high') redCont = Math.max(redCont, REDUCTIONS.CONTRIBUTION.INCOME_HIGH);
        else if (incomeLevel === 'mid') redCont = Math.max(redCont, REDUCTIONS.CONTRIBUTION.INCOME_MID);
        if (publicService) redCont = Math.max(redCont, REDUCTIONS.CONTRIBUTION.PUBLIC_SERVICE);
        if (volunteering) redCont = Math.max(redCont, REDUCTIONS.CONTRIBUTION.VOLUNTEERING);
        red += redCont;

        let redEntry = 0;
        if (visaType === 'family') redEntry = Math.max(redEntry, REDUCTIONS.ENTRY.FAMILY_BRITISH);
        if (visaType === 'bno') redEntry = Math.max(redEntry, REDUCTIONS.ENTRY.BNO);
        if (visaType === 'global_talent') redEntry = Math.max(redEntry, REDUCTIONS.ENTRY.GLOBAL_TALENT);
        red += redEntry;

        let pen = 0;
        if (publicFunds === 'low') pen += PENALTIES.PUBLIC_FUNDS_LOW;
        if (publicFunds === 'high') pen += PENALTIES.PUBLIC_FUNDS_HIGH;
        if (immigrationBreach) pen += PENALTIES.IMMIGRATION_BREACH;

        const qualifyingYears = Math.max(0, baseline - red + pen);
        const entry = new Date(entryDate);
        const eligibilityDate = new Date(entry);
        eligibilityDate.setFullYear(entry.getFullYear() + qualifyingYears);

        // Render Results
        document.getElementById('out-date').textContent = eligibilityDate.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
        document.getElementById('out-years').textContent = qualifyingYears;
        document.getElementById('out-baseline').textContent = baseline;

        const breakdown = document.getElementById('out-breakdown');
        breakdown.innerHTML = '';

        if (red > 0) {
            breakdown.innerHTML += `<div class="breakdown-row positive"><span>Reductions Earned</span><span>-${red} Years</span></div>`;
        }
        if (pen > 0) {
            breakdown.innerHTML += `<div class="breakdown-row negative"><span>Penalties Applied</span><span>+${pen} Years</span></div>`;
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('ilr-wizard-container')) {
        window.ilrWizard = new ILRWizard();
    }

    // --- Sponsor Checker Logic ---
    const sponsorInput = document.getElementById('sponsor-input');
    const sponsorBtn = document.getElementById('sponsor-btn');
    const sponsorResults = document.getElementById('sponsor-results');

    if (sponsorInput && sponsorBtn && sponsorResults) {
        let sponsorData = [];
        let isLoading = false;
        let hasLoaded = false;

        async function loadSponsorData() {
            if (hasLoaded || isLoading) return;

            isLoading = true;
            sponsorResults.innerHTML = `<div class="placeholder-text">Loading official register (16MB)... please wait.</div>`;

            try {
                const response = await fetch('sponsors.json');
                if (!response.ok) throw new Error("Failed to load data");
                sponsorData = await response.json();

                // Load Metadata
                try {
                    const metaResponse = await fetch('metadata.json');
                    if (metaResponse.ok) {
                        const meta = await metaResponse.json();
                        const dateEl = document.getElementById('data-date');
                        if (dateEl && meta.last_updated) {
                            dateEl.textContent = meta.last_updated;
                        }
                    }
                } catch (err) {
                    console.warn("Could not load metadata", err);
                }

                hasLoaded = true;
                sponsorResults.innerHTML = `<div class="placeholder-text">Database loaded. Ready to search.</div>`;
                console.log(`Loaded ${sponsorData.length} sponsors.`);
            } catch (e) {
                console.error(e);
                sponsorResults.innerHTML = `<div class="placeholder-text" style="color:red">Error loading database. Please refresh.</div>`;
            } finally {
                isLoading = false;
            }
        }

        // Load data when user interacts
        sponsorInput.addEventListener('focus', loadSponsorData);

        function searchSponsors() {
            const query = sponsorInput.value.toLowerCase().trim();
            if (!query) return;

            if (!hasLoaded) {
                loadSponsorData().then(() => searchSponsors());
                return;
            }

            sponsorResults.innerHTML = '';
            // Limit to top 50 results for performance
            const results = sponsorData.filter(s => s.name.toLowerCase().includes(query)).slice(0, 50);

            if (results.length === 0) {
                sponsorResults.innerHTML = `<div class="placeholder-text">No sponsors found matching "${query}".</div>`;
                return;
            }

            results.forEach(s => {
                const el = document.createElement('div');
                el.className = 'sponsor-item';
                el.innerHTML = `
                    <div class="sponsor-info">
                        <h4>${s.name}</h4>
                        <p>${s.city} • ${s.route}</p>
                    </div>
                    <span class="badge licensed">Licensed</span>
                `;
                sponsorResults.appendChild(el);
            });
        }

        sponsorBtn.onclick = searchSponsors;
        sponsorInput.onkeypress = (e) => {
            if (e.key === 'Enter') searchSponsors();
        };
    }
});
