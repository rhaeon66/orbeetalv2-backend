from django.core.management.base import BaseCommand

from api.models import (
    Client,
    Department,
    FAQ,
    HomepageContent,
    Product,
    Project,
    Service,
    Slide,
    TeamMember,
    Testimonial,
)

SLIDES = [
    {
        "name": "Web Development",
        "headline": "Responsive Websites",
        "accent": "Built to Scale Your Business",
        "description": (
            "Enterprise-grade web solutions engineered for performance, security, "
            "and growth — from concept to deployment."
        ),
        "image_fallback": "/images/web.png",
        "primary_cta_label": "Meet Our Experts",
        "primary_cta_href": "/contact",
        "secondary_cta_label": "View Our Work",
        "secondary_cta_href": "/portfolio",
    },
    {
        "name": "Mobile Engineering",
        "headline": "Mobile Applications",
        "accent": "Future-Ready by Design",
        "description": (
            "Native and cross-platform apps that deliver seamless experiences "
            "across every device your customers use."
        ),
        "image_fallback": "/images/mobile.png",
        "primary_cta_label": "Start a Project",
        "primary_cta_href": "/contact",
        "secondary_cta_label": "Explore Services",
        "secondary_cta_href": "/services",
    },
    {
        "name": "Cloud Infrastructure",
        "headline": "Cloud Solutions",
        "accent": "Scale Without Limits",
        "description": (
            "Secure, resilient cloud architecture that grows with your business "
            "— optimized for speed and reliability."
        ),
        "image_fallback": "/images/cloud.png",
        "primary_cta_label": "Talk to Us",
        "primary_cta_href": "/contact",
        "secondary_cta_label": "Learn More",
        "secondary_cta_href": "/services",
    },
    {
        "name": "Digital Growth",
        "headline": "Digital Marketing",
        "accent": "Drive Measurable Results",
        "description": (
            "Data-driven strategies that amplify your brand, generate qualified "
            "leads, and accelerate revenue growth."
        ),
        "image_fallback": "/images/dig.png",
        "primary_cta_label": "Get Started",
        "primary_cta_href": "/contact",
        "secondary_cta_label": "See Portfolio",
        "secondary_cta_href": "/portfolio",
    },
    {
        "name": "Artificial Intelligence",
        "headline": "AI-Powered Solutions",
        "accent": "Smarter Business Operations",
        "description": (
            "Intelligent automation and AI integrations that transform workflows "
            "and unlock competitive advantage."
        ),
        "image_fallback": "/images/chatbot.png",
        "primary_cta_label": "Meet Our Experts",
        "primary_cta_href": "/contact",
        "secondary_cta_label": "Explore More",
        "secondary_cta_href": "/services",
    },
]

PROJECTS = [
    {
        "name": "Education System Software",
        "description": "Full school management suite",
        "category": Project.CATEGORY_OWN,
        "url": "",
        "features": [
            "Student Management",
            "Teacher Management",
            "Administration Management",
            "Exam Management",
            "Class Management",
        ],
        "image_fallback": "/images/mockups/education.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "Rahik Ibne Forman",
        "related_role": "Supervisor",
        "related_image_fallback": "/images/rahik.jpeg",
    },
    {
        "name": "Plant Paradise",
        "description": "Smart plant care and disease detection system",
        "category": Project.CATEGORY_PARTNERSHIP,
        "url": "",
        "features": [
            "Plant Identification",
            "Disease Detection",
            "Growth Monitoring",
            "Watering & Care Alerts",
            "Fertilizer Recommendations",
        ],
        "image_fallback": "/images/mockups/plant.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "Mst. Samia Aktar Sathi",
        "related_role": "",
        "related_image_fallback": "/images/mockups/sathi.jpeg",
    },
    {
        "name": "Munabooks Service",
        "description": "Orders, inventory and analytics",
        "category": Project.CATEGORY_CLIENT,
        "url": "https://www.munabooks.com",
        "features": ["Orders", "Products", "Reports", "Users"],
        "image_fallback": "/images/mockups/munabooks.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "Muslim Ummah of North America",
        "related_role": "",
        "related_image_fallback": "/images/mockups/muna-logo.png",
    },
    {
        "name": "Burial Management System",
        "description": "Graveyard, funeral, and record management",
        "category": Project.CATEGORY_CLIENT,
        "url": "https://www.munacemetery.com",
        "features": [
            "Grave Plot Allocation",
            "Funeral Scheduling",
            "Deceased Records Management",
            "Payment & Documentation",
        ],
        "image_fallback": "/images/mockups/cemetery.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "Muslim Ummah of North America",
        "related_role": "",
        "related_image_fallback": "/images/mockups/muna-logo.png",
    },
    {
        "name": "Airy Products",
        "description": "Cleanroom, HVAC, and air filtration solutions",
        "category": Project.CATEGORY_CLIENT,
        "url": "https://www.airyfiltration.com.bd",
        "features": [
            "Cleanroom Equipment",
            "HVAC Systems",
            "Air Filtration Units",
            "Environmental Monitoring",
        ],
        "image_fallback": "/images/mockups/airy.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "Airy International",
        "related_role": "",
        "related_image_fallback": "/images/mockups/airy-logo.webp",
    },
    {
        "name": "Cleanroom Products",
        "description": "Cleanroom, HVAC, and air filtration solutions",
        "category": Project.CATEGORY_CLIENT,
        "url": "https://www.cleanroomac.com",
        "features": [
            "Cleanroom Equipment",
            "HVAC Systems",
            "Air Filtration Units",
            "Environmental Monitoring",
        ],
        "image_fallback": "/images/mockups/cleanroom.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "Cleanroom AC",
        "related_role": "",
        "related_image_fallback": "/images/mockups/cleanroom-logo.webp",
    },
    {
        "name": "RUET Reporters Unity",
        "description": "University News Portal",
        "category": Project.CATEGORY_CLIENT,
        "url": "https://www.rru24.com",
        "features": [
            "Latest University News",
            "Event Updates",
            "Student Contributions",
            "Campus Announcements",
        ],
        "image_fallback": "/images/mockups/ruet-logo.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "RUET Reporters Unity",
        "related_role": "",
        "related_image_fallback": "/images/mockups/ruet-logo-small.svg",
    },
    {
        "name": "July Heroes",
        "description": "Martyrs, Injured and Murderers of 2024 July Revolution",
        "category": Project.CATEGORY_CLIENT,
        "url": "https://www.julyheroes.com",
        "features": ["Martyrs", "Murderers", "Injured", "Events"],
        "image_fallback": "/images/mockups/july.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "July Heroes",
        "related_role": "",
        "related_image_fallback": "/images/july.svg",
    },
    {
        "name": "Airy Filtration",
        "description": "Cleanroom, HVAC, and air filtration solutions",
        "category": Project.CATEGORY_CLIENT,
        "url": "https://www.airyfiltration.com.bd",
        "features": [
            "Cleanroom Equipment",
            "HVAC Systems",
            "Air Filtration Units",
            "Environmental Monitoring",
        ],
        "image_fallback": "/images/mockups/airy-filtration.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "Airy International",
        "related_role": "",
        "related_image_fallback": "/images/mockups/airy-logo.webp",
    },
    {
        "name": "CloudX Academy",
        "description": "Cloud Computing and AI Training",
        "category": Project.CATEGORY_CLIENT,
        "url": "https://www.cloudx.academy",
        "features": ["Cloud Computing", "AI Training", "Certification", "Hands-on Labs"],
        "image_fallback": "/images/mockups/cloudx.png",
        "logo_fallback": "/logo-small.jpeg",
        "related_name": "CloudX Academy",
        "related_role": "",
        "related_image_fallback": "/images/cloudx.jpg",
    },
]

SERVICES = [
    {
        "name": "Software Development",
        "description": (
            "Transform your digital landscape with our custom software solutions "
            "that put your business ahead of the curve."
        ),
        "content": [
            "Leveraging technologies like .NET, Java, PHP, Python, Ruby, and MySQL.",
            "Agile methodology for flexibility and rapid development.",
            "Scalable, secure, and high-performing software.",
            "Quality assurance and timely delivery.",
        ],
        "image_fallback": "/images/software.png",
    },
    {
        "name": "AI Solutions",
        "description": (
            "Leverage artificial intelligence to enhance your business operations "
            "and drive innovation."
        ),
        "content": [
            "Machine learning to improve data insights.",
            "Natural language processing for better user interaction.",
            "Data analytics to help make data-driven decisions.",
            "Enhance efficiency and innovation.",
        ],
        "image_fallback": "/images/chatbot.png",
    },
    {
        "name": "Digital Marketing",
        "description": (
            "Boost your online presence with targeted digital marketing strategies "
            "designed to grow your brand."
        ),
        "content": [
            "SEO and SEM for better search rankings.",
            "Social media marketing to increase engagement.",
            "Content creation to drive traffic and awareness.",
            "Strategies to improve brand visibility and sales.",
        ],
        "image_fallback": "/images/dig.png",
    },
    {
        "name": "Product Design",
        "description": (
            "Create innovative, user-centered designs that drive customer "
            "satisfaction and business success."
        ),
        "content": [
            "End-to-end product design from wireframing to testing.",
            "User testing and implementation for seamless user experiences.",
            "Prototyping to validate concepts.",
        ],
        "image_fallback": "/images/product-design.jpg",
    },
    {
        "name": "Web Development",
        "description": (
            "Build responsive, high-performance websites that engage your audience "
            "and drive conversions."
        ),
        "content": [
            "Front-end and back-end development for a full-stack solution.",
            "E-commerce integration to boost sales.",
            "CMS integration for easy content management.",
            "SEO optimization to ensure search engine visibility.",
        ],
        "image_fallback": "/images/web-development.svg",
    },
    {
        "name": "Cyber Security",
        "description": (
            "Protect your business with comprehensive cyber security solutions "
            "tailored to your needs."
        ),
        "content": [
            "Risk assessments to identify vulnerabilities.",
            "Threat detection and response systems.",
            "Compliance with industry regulations.",
        ],
        "image_fallback": "/images/cyber.png",
    },
]

TEAM_MEMBERS = [
    {
        "name": "Saiful Islam",
        "role": "Director",
        "email": "saiful@orbeetal.com",
        "bio": (
            "A visionary leader with expertise in financial strategy and business "
            "growth. Passionate about building sustainable business models and "
            "driving organizational excellence."
        ),
        "image_fallback": "/images/saif.jpeg",
        "experience": 5,
        "projects": 20,
        "expertise": [
            "Financial Strategy",
            "Business Development",
            "Investment Planning",
            "Risk Analysis",
        ],
        "department_name": "Finance",
        "department_description": (
            "Ensuring financial stability and strategic growth for the organization."
        ),
        "department_roles": ["Budgeting", "Auditing", "Risk Management"],
        "department_productions": ["Annual Report 2024", "Cost Optimization Plan"],
    },
    {
        "name": "Hasibul Hasan Sifat",
        "role": "Director",
        "email": "sifat@orbeetal.com",
        "bio": (
            "An operations mastermind focused on streamlining processes and "
            "maximizing efficiency. Expert in strategic planning and resource "
            "optimization."
        ),
        "image_fallback": "/images/sifat.jpeg",
        "experience": 4,
        "projects": 18,
        "expertise": [
            "Operations Management",
            "Process Optimization",
            "Strategic Planning",
            "Team Leadership",
        ],
        "department_name": "Operation",
        "department_description": "Strategizing for a brighter, more efficient future.",
        "department_roles": [
            "Long-term Strategy",
            "Resource Allocation",
            "Policy Development",
        ],
        "department_productions": ["Vision 2030 Roadmap", "Urban Growth Plan"],
    },
    {
        "name": "Muktadir Hasan Sayem",
        "role": "Director",
        "email": "sayem@orbeetal.com",
        "bio": (
            "A cybersecurity expert dedicated to protecting digital assets and "
            "ensuring data integrity. Specialized in threat detection and security "
            "architecture."
        ),
        "image_fallback": "/images/sayem.jpeg",
        "experience": 4,
        "projects": 15,
        "expertise": [
            "Cybersecurity",
            "Threat Analysis",
            "Network Security",
            "Penetration Testing",
        ],
        "department_name": "Cyber",
        "department_description": "Securing digital landscapes for today and tomorrow.",
        "department_roles": ["Threat Monitoring", "Data Security", "Incident Response"],
        "department_productions": ["CyberShield AI", "Security Awareness Program"],
    },
    {
        "name": "Musanna Galib",
        "role": "Director",
        "email": "galib@orbeetal.com",
        "bio": (
            "An innovative thinker driving product innovation and research "
            "initiatives. Passionate about leveraging emerging technologies to "
            "solve complex problems."
        ),
        "image_fallback": "/images/galib.jpeg",
        "experience": 3,
        "projects": 12,
        "expertise": [
            "Product Innovation",
            "AI/ML Research",
            "Tech Strategy",
            "R&D Leadership",
        ],
        "department_name": "Planning",
        "department_description": "Innovating the future through research and technology.",
        "department_roles": ["Product Innovation", "AI Research", "Tech Optimization"],
        "department_productions": [
            "AI Engine v2.0",
            "NextGen Robotics",
            "Green Tech Solutions",
        ],
    },
    {
        "name": "Rahik Ibne Forman",
        "role": "Director",
        "email": "rahik@orbeetal.com",
        "bio": (
            "A technology leader with deep expertise in IT infrastructure and cloud "
            "solutions. Committed to delivering robust and scalable technology "
            "solutions."
        ),
        "image_fallback": "/images/rahik.jpeg",
        "experience": 4,
        "projects": 25,
        "expertise": [
            "Cloud Architecture",
            "Full-Stack Development",
            "DevOps",
            "System Design",
        ],
        "department_name": "Information Technology",
        "department_description": "Harnessing the power of technology to drive business.",
        "department_roles": ["Infrastructure", "Cloud Solutions", "IT Support"],
        "department_productions": ["Cloud Migration 2024", "Enterprise IT Helpdesk"],
    },
    {
        "name": "Sayed Muhit Al Rafi",
        "role": "Director",
        "email": "rafi@orbeetal.com",
        "bio": (
            "A creative product designer with a keen eye for user experience. "
            "Transforms complex ideas into elegant, user-friendly digital products."
        ),
        "image_fallback": "/images/sayed.jpg",
        "experience": 4,
        "projects": 22,
        "expertise": [
            "Product Design",
            "UX/UI Design",
            "Prototyping",
            "User Research",
        ],
        "department_name": "Product",
        "department_description": "Turning ideas into market-ready products.",
        "department_roles": ["Product Design", "Prototyping", "User Research"],
        "department_productions": ["SmartWear Devices", "Mobile App Suite"],
    },
    {
        "name": "Shahadat Hossain",
        "role": "Director",
        "email": "shahadat@orbeetal.com",
        "bio": (
            "A marketing strategist with proven success in brand building and "
            "digital campaigns. Expert in creating compelling narratives that "
            "resonate with audiences."
        ),
        "image_fallback": "/images/shahadat.jpeg",
        "experience": 5,
        "projects": 30,
        "expertise": [
            "Digital Marketing",
            "Brand Strategy",
            "Content Marketing",
            "SEO/SEM",
        ],
        "department_name": "Marketing",
        "department_description": "Amplifying your brand's voice in the digital world.",
        "department_roles": [
            "Brand Strategy",
            "Campaign Management",
            "Customer Engagement",
        ],
        "department_productions": ["Digital Ad Campaigns", "Global Branding Strategy"],
    },
]

TESTIMONIALS = [
    {
        "name": "Md. Mayeen Uddin",
        "role": "Ex President, RUET Reporters Unity",
        "quote": (
            "As President of RUET Reporters Unity, I commend Orbeetal for their "
            "outstanding work in creating rru24.com. Their innovative web "
            "development and dedicated support have given us a dynamic platform "
            "to share truthful journalism and connect with our community. Thank "
            "you, Orbeetal, for bringing our vision to life!"
        ),
        "image_fallback": "/images/mayeen.png",
    },
    {
        "name": "Rakibul Hasan Nur",
        "role": "President, RUET Reporters Unity",
        "quote": (
            "As the current President of RUET Reporters Unity, I deeply "
            "appreciate Orbeetal's continued support in maintaining and "
            "upgrading rru24.com. Their reliable IT solutions and quick response "
            "to our needs ensure that our platform runs smoothly, empowering us "
            "to deliver accurate news and uphold the values of responsible "
            "journalism. We are grateful for their partnership in strengthening "
            "our digital presence."
        ),
        "image_fallback": "/images/rakibul.jpg",
    },
    {
        "name": "Mst. Samia Aktar Sathi",
        "role": "Plant Paradise",
        "quote": (
            "Orbeetal believed in my idea for Plant Paradise and supported me to "
            "turn it into a growing project. Their honest values and dedication "
            "to empowering entrepreneurs inspire me to dream bigger and create "
            "real impact."
        ),
        "image_fallback": "/images/mockups/sathi.jpeg",
    },
]

FAQS = [
    {
        "name": "What services does Orbeetal provide?",
        "answer": (
            "We specialize in end-to-end digital solutions including web & "
            "mobile app development, AI-powered systems, cloud solutions, "
            "cybersecurity, and digital transformation consulting."
        ),
    },
    {
        "name": "Why should I choose Orbeetal for my project?",
        "answer": (
            "Our expert team combines innovation, technical excellence, and "
            "customer-centric strategy to deliver solutions that are scalable, "
            "secure, and aligned with your long-term growth."
        ),
    },
    {
        "name": "How does Orbeetal ensure project quality?",
        "answer": (
            "We follow strict quality assurance processes, agile methodologies, "
            "and continuous testing to ensure reliable, high-performance solutions."
        ),
    },
    {
        "name": "Do you offer ongoing support and maintenance?",
        "answer": (
            "Yes. We provide 24/7 technical support, regular maintenance, and "
            "system upgrades to keep your business running without disruptions."
        ),
    },
    {
        "name": "Can Orbeetal handle enterprise-level projects?",
        "answer": (
            "Absolutely. Our expertise spans startups to large enterprises, "
            "delivering scalable and secure enterprise-grade applications "
            "tailored to your business needs."
        ),
    },
]

PRODUCTS = [
    {
        "name": "Note Sharing App",
        "description": (
            "A powerful note-sharing platform that helps teams collaborate "
            "efficiently. Share, edit, and organize notes seamlessly with "
            "real-time sync."
        ),
        "url": "",
        "features": ["Award Winning", "24/7 Support", "Professional Staff", "Fair Prices"],
        "image_fallback": "/images/note.png",
        "screen_image_fallback": "/images/notess2.png",
    },
    {
        "name": "Task Manager Pro",
        "description": (
            "Stay organized and productive with Task Manager Pro. Assign tasks, "
            "track deadlines, and boost productivity effortlessly."
        ),
        "url": "",
        "features": [
            "Cross-Platform",
            "Secure Data",
            "Customizable Dashboard",
            "Cloud Backup",
        ],
        "image_fallback": "/images/task.png",
        "screen_image_fallback": "/images/taskss.png",
    },
    {
        "name": "E-Learning Hub",
        "description": (
            "An intuitive e-learning solution for schools and businesses. Create, "
            "manage, and deliver courses with ease."
        ),
        "url": "",
        "features": [
            "HD Video Classes",
            "Gamified Learning",
            "Certificate Issuing",
            "Scalable Solution",
        ],
        "image_fallback": "/images/learning.jpg",
        "screen_image_fallback": "/images/learningss.png",
    },
    {
        "name": "Finance Tracker",
        "description": (
            "Track expenses, set budgets, and visualize your financial health. "
            "Finance Tracker makes money management simple."
        ),
        "url": "",
        "features": [
            "Expense Tracking",
            "Budget Alerts",
            "AI Insights",
            "Multi-Currency Support",
        ],
        "image_fallback": "/images/finance.jpg",
        "screen_image_fallback": "/images/financess.png",
    },
]

DEPARTMENTS = [
    {
        "name": "Planning",
        "description": "Innovating the future through research and technology.",
        "icon_fallback": "/images/research.png",
        "director_name": "Musanna Galib",
        "director_image_fallback": "/images/galib.jpeg",
        "roles": ["Product Innovation", "AI Research", "Tech Optimization"],
        "productions": ["AI Engine v2.0", "NextGen Robotics", "Green Tech Solutions"],
    },
    {
        "name": "Finance",
        "description": "Ensuring financial stability and strategic growth.",
        "icon_fallback": "/images/finance.png",
        "director_name": "Saiful Islam",
        "director_image_fallback": "/images/saif.jpeg",
        "roles": ["Budgeting", "Auditing", "Risk Management"],
        "productions": ["Annual Report 2024", "Cost Optimization Plan"],
    },
    {
        "name": "Operation",
        "description": "Strategizing for a brighter, more efficient future.",
        "icon_fallback": "/images/planning.jpg",
        "director_name": "Hasibul Hasan Sifat",
        "director_image_fallback": "/images/sifat.jpeg",
        "roles": ["Long-term Strategy", "Resource Allocation", "Policy Development"],
        "productions": ["Vision 2030 Roadmap", "Urban Growth Plan"],
    },
    {
        "name": "Cyber",
        "description": "Securing digital landscapes for today and tomorrow.",
        "icon_fallback": "/images/cyber.png",
        "director_name": "Muktadir Hasan Sayem",
        "director_image_fallback": "/images/sayem.jpeg",
        "roles": ["Threat Monitoring", "Data Security", "Incident Response"],
        "productions": ["CyberShield AI", "Security Awareness Program"],
    },
    {
        "name": "Marketing",
        "description": "Amplifying your brand's voice in the digital world.",
        "icon_fallback": "/images/marketing.png",
        "director_name": "Shahadat Hossain",
        "director_image_fallback": "/images/shahadat.jpeg",
        "roles": ["Brand Strategy", "Campaign Management", "Customer Engagement"],
        "productions": ["Digital Ad Campaigns", "Global Branding Strategy"],
    },
    {
        "name": "Information Technology",
        "description": "Harnessing the power of technology to drive business.",
        "icon_fallback": "/images/it.png",
        "director_name": "Rahik Ibne Forman",
        "director_image_fallback": "/images/rahik.jpeg",
        "roles": ["Infrastructure", "Cloud Solutions", "IT Support"],
        "productions": ["Cloud Migration 2024", "Enterprise IT Helpdesk"],
    },
    {
        "name": "Product",
        "description": "Turning ideas into market-ready products.",
        "icon_fallback": "/images/graphics.png",
        "director_name": "Sayed Muhit Al Rafi",
        "director_image_fallback": "/images/sayed.jpg",
        "roles": ["Product Design", "Prototyping", "User Research"],
        "productions": ["SmartWear Devices", "Mobile App Suite"],
    },
]

CLIENTS = [
    {"name": "Ruet Reporters Unity", "url": "", "logo_fallback": "/images/client.jpg"},
    {
        "name": "Airy International",
        "url": "",
        "logo_fallback": "/images/mockups/airy-logo.webp",
    },
    {
        "name": "Cleanroom AC",
        "url": "",
        "logo_fallback": "/images/mockups/cleanroom-logo.webp",
    },
    {"name": "MUNA", "url": "", "logo_fallback": "/images/mockups/muna-logo.png"},
    {"name": "CloudX Academy", "url": "", "logo_fallback": "/images/cloudx.png"},
    {"name": "July Heroes", "url": "", "logo_fallback": "/images/july.svg"},
]

HOMEPAGE = {
    "stats": [
        {
            "value": 50,
            "suffix": "+",
            "label": "Happy Clients",
            "description": "Partners who trust us long-term",
            "featured": False,
        },
        {
            "value": 120,
            "suffix": "+",
            "label": "Projects Delivered",
            "description": "Successfully shipped worldwide",
            "featured": True,
        },
        {
            "value": 15,
            "suffix": "+",
            "label": "Active Projects",
            "description": "Currently in development",
            "featured": False,
        },
    ],
    "about_eyebrow": "About Us",
    "about_title": "One of the Fastest Ways to",
    "about_highlight": "Business Growth",
    "about_body": (
        "Orbeetal is a forward-thinking software company dedicated to "
        "building smart, impactful technology. We specialize in web "
        "development, UI/UX design, cybersecurity, and digital marketing — "
        "empowering businesses through innovation and intelligent "
        "solutions. Our mission is simple: solve real-world problems with "
        "purpose-driven tech that makes a difference."
    ),
    "about_image_fallback": "/images/teams-1.png",
    "about_cta_label": "Get In Touch",
    "about_cta_href": "/contact",
    "about_badge_value": "5+ Years",
    "about_badge_label": "of engineering excellence",
    "about_highlights": [
        {"label": "Innovation-led", "text": "Modern stacks & clean architecture"},
        {"label": "Trusted delivery", "text": "Secure, reliable, on time"},
        {"label": "Growth focused", "text": "Built to scale with you"},
    ],
    "why_eyebrow": "Why Choose Us",
    "why_title": "We Are Here to Grow Your",
    "why_highlight": "Business Exponentially",
    "why_subtitle": (
        "A single partner for strategy, design, engineering and growth — "
        "committed to outcomes that move your business forward."
    ),
    "why_image_fallback": "/images/teams-2.png",
    "why_items": [
        {
            "title": "Innovative Solutions",
            "description": (
                "We design and deliver modern digital products powered by the "
                "latest technologies to keep your business ahead of the curve."
            ),
            "icon": "/images/web-design.svg",
        },
        {
            "title": "Expert & Dedicated Team",
            "description": (
                "Our passionate professionals bring deep expertise in software "
                "engineering, design, and strategy to every project we take on."
            ),
            "icon": "/images/ui-ux.svg",
        },
        {
            "title": "End-to-End Service",
            "description": (
                "From idea to execution, we handle the full development lifecycle "
                "— ensuring seamless delivery and long-term scalability."
            ),
            "icon": "/images/web-development.svg",
        },
        {
            "title": "Reliable 24/7 Support",
            "description": (
                "We provide round-the-clock technical support and maintenance to "
                "ensure your systems are always running at their best."
            ),
            "icon": "/images/cyber-security.svg",
        },
        {
            "title": "Digital Growth Strategy",
            "description": (
                "Beyond development, we help brands grow through digital "
                "transformation, performance marketing, and customer engagement."
            ),
            "icon": "/images/digital-marketing.svg",
        },
    ],
    "method_eyebrow": "How We Work",
    "method_title": "Our",
    "method_highlight": "IT Methodology",
    "method_subtitle": (
        "A proven, transparent process that takes your idea from concept to a "
        "polished, scalable product — on time and on budget."
    ),
    "method_steps": [
        {
            "title": "Discover",
            "desc": "Understand the problem, users, and requirements before a line of code.",
            "points": [
                "Business & user research",
                "Requirements discovery",
                "Problem definition",
            ],
        },
        {
            "title": "Plan",
            "desc": "Turn discovery into a clear roadmap, architecture, and scope.",
            "points": [
                "Project roadmap",
                "Technical planning",
                "Architecture & scope",
            ],
        },
        {
            "title": "Design",
            "desc": "Research-driven UX and UI systems that convert.",
            "points": [
                "UX research",
                "UI design",
                "Design system",
                "Prototyping",
            ],
        },
        {
            "title": "Develop",
            "desc": "Clean, scalable engineering on modern stacks.",
            "points": [
                "Frontend & backend",
                "API development",
                "Database integration",
                "Code reviews",
            ],
        },
        {
            "title": "Test & Deploy",
            "desc": "Prove quality, then ship with confidence.",
            "points": [
                "QA & testing",
                "Security validation",
                "CI/CD",
                "Production deployment",
            ],
        },
        {
            "title": "Maintain & Scale",
            "desc": "Keep the product healthy as usage and scope grow.",
            "points": [
                "Monitoring",
                "Bug fixes",
                "Performance optimization",
                "Technical support",
                "Scaling",
            ],
        },
    ],
    "expertise_eyebrow": "Services",
    "expertise_title": "Our",
    "expertise_highlight": "Expertise",
    "expertise_subtitle": (
        "A full spectrum of digital capabilities — combined under one roof to "
        "take your product from idea to impact."
    ),
    "expertise_items": [
        {
            "title": "App Development",
            "description": (
                "High-performance, scalable mobile apps tailored to your "
                "business — seamless design and robust functionality across iOS "
                "and Android."
            ),
            "icon": "/images/mobile-development.png",
        },
        {
            "title": "UI/UX Design",
            "description": (
                "Research-driven interfaces and design systems that are "
                "intuitive, accessible, and crafted to convert visitors into "
                "loyal customers."
            ),
            "icon": "/images/ui-ux.svg",
        },
        {
            "title": "Web Development",
            "description": (
                "Fast, secure, and SEO-ready websites and web apps built on "
                "modern frameworks — engineered for performance and growth."
            ),
            "icon": "/images/web-development.svg",
        },
        {
            "title": "Cyber Security",
            "description": (
                "End-to-end protection with threat monitoring, audits, and "
                "secure architecture to keep your data and users safe around "
                "the clock."
            ),
            "icon": "/images/cyber-security.svg",
        },
        {
            "title": "Digital Marketing",
            "description": (
                "Data-driven campaigns, SEO, and content strategy that amplify "
                "your brand, generate qualified leads, and accelerate revenue."
            ),
            "icon": "/images/digital-marketing.svg",
        },
        {
            "title": "AI Powered Solutions",
            "description": (
                "Predictive analytics, NLP, computer vision, and automation that "
                "drive smarter decisions and unlock new opportunities for growth."
            ),
            "icon": "/images/ai.png",
        },
    ],
}


def _is_empty(value):
    return value in ("", None, [], {})


def upsert(model, payload, sort_order, fill_if_empty="description"):
    obj = model.objects.filter(name=payload["name"]).first()
    if obj is None:
        model.objects.create(sort_order=sort_order, is_active=True, **payload)
        return "created"
    if not _is_empty(getattr(obj, fill_if_empty, None)):
        return "skipped"
    for key, value in payload.items():
        if key == "name":
            continue
        setattr(obj, key, value)
    obj.sort_order = sort_order
    obj.save()
    return "updated"


class Command(BaseCommand):
    help = "Seed catalog rows that match the current public site."

    def handle(self, *args, **options):
        created_total = 0
        updated_total = 0

        for index, item in enumerate(SLIDES):
            result = upsert(Slide, item, index, fill_if_empty="headline")
            if result == "created":
                created_total += 1
            elif result == "updated":
                updated_total += 1

        for index, item in enumerate(PROJECTS):
            result = upsert(Project, item, index, fill_if_empty="description")
            if result == "created":
                created_total += 1
            elif result == "updated":
                updated_total += 1

        for index, item in enumerate(SERVICES):
            result = upsert(Service, item, index, fill_if_empty="description")
            if result == "created":
                created_total += 1
            elif result == "updated":
                updated_total += 1

        for index, item in enumerate(TEAM_MEMBERS):
            result = upsert(TeamMember, item, index, fill_if_empty="bio")
            if result == "created":
                created_total += 1
            elif result == "updated":
                updated_total += 1

        for index, item in enumerate(TESTIMONIALS):
            result = upsert(Testimonial, item, index, fill_if_empty="quote")
            if result == "created":
                created_total += 1
            elif result == "updated":
                updated_total += 1

        for index, item in enumerate(FAQS):
            result = upsert(FAQ, item, index, fill_if_empty="answer")
            if result == "created":
                created_total += 1
            elif result == "updated":
                updated_total += 1

        for index, item in enumerate(PRODUCTS):
            result = upsert(Product, item, index, fill_if_empty="description")
            if result == "created":
                created_total += 1
            elif result == "updated":
                updated_total += 1

        for index, item in enumerate(DEPARTMENTS):
            result = upsert(Department, item, index, fill_if_empty="description")
            if result == "created":
                created_total += 1
            elif result == "updated":
                updated_total += 1

        for index, item in enumerate(CLIENTS):
            result = upsert(Client, item, index, fill_if_empty="logo_fallback")
            if result == "created":
                created_total += 1
            elif result == "updated":
                updated_total += 1

        homepage, homepage_created = HomepageContent.objects.get_or_create(
            pk=1, defaults=HOMEPAGE
        )
        if homepage_created:
            created_total += 1
        elif _is_empty(homepage.about_body):
            for key, value in HOMEPAGE.items():
                setattr(homepage, key, value)
            homepage.save()
            updated_total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalog seed complete ({created_total} created, {updated_total} updated)."
            )
        )
