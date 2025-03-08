# MIND YOUR OWN BUSINESS
![Responsive](app/static/images/responsive.png)
[Click here to view the live website](https://mind-your-own-business-5f784ff22ecb.herokuapp.com/)


# (Overview) Mind Your Own Business

**Mind Your Own Business** is an online platform designed to empower **sole traders and small businesses** by making promotion simple, effective, and hassle-free.

## 🚀 Helping Small Businesses Get Noticed  

As a former self-employed business owner running **DL Cleaners**, I quickly realized that the hardest part of growing a business wasn't the work itself—it was getting noticed. Finding customers, promoting deals, and building a local presence often felt like an uphill battle.  

That's why I created **Mind Your Own Business**—a platform for **small business owners**, including **cleaners, nail technicians, personal trainers, landscapers, childminders, and tradespeople**, to **showcase their services and attract customers** without relying on expensive advertising.

## 🔹 How It Works  

- ✅ **Create a Business Profile** – Register and build a profile to introduce your business, services, and contact details.  
- ✅ **Promote Your Services** – Easily add deals and special offers to attract local customers.  
- ✅ **Browse Local Businesses** – Users can explore promotions and discover trusted businesses in their area.  
- ✅ **Exclusive Access for Registered Users** – While promotions are visible to everyone, only registered members can view business profiles and connect with owners.  

## 💡 Why Choose Mind Your Own Business?  

Whether you're a **mobile hairdresser offering discounts, a cleaner looking for more clients, or a builder running a limited-time deal**, **Mind Your Own Business** helps you connect with the right customers and grow your business effortlessly.

📢 **Join today and start promoting your business!** [Join Now](#)

## 🔑 Key Features  

- **🆓 Free Business Listings** – Create a profile and showcase your business at no cost.  
- **📢 Easy Promotion** – Post deals, discounts, and promotions to attract customers.  
- **📍 Local Business Discovery** – Users can find and connect with trusted businesses in their area.  
- **🔐 Member-Only Access** – Only registered users can view full business profiles and connect directly.  
- **💬 Customer Engagement** – Encourage reviews and feedback to build trust with potential clients.  
- **📱 Mobile-Friendly** – Seamlessly browse and manage your business from any device.  
- **🔍 Search & Filter Options** – Easily find businesses and promotions based on category and location.  

## 🔮 Future Features  

🚧 *Upcoming enhancements to improve user experience and business visibility:*  

- **📍 Location-Based Listings** – Businesses and promotions will be displayed only within a **10-mile radius** of the user’s location.  
- **🔎 Advanced Search & Filters** – Users will be able to filter businesses by category, ratings, and proximity.  
- **⭐ Customer Reviews & Ratings** – Implementing a review system where customers can leave feedback and rate businesses.  
- **📅 Event & Booking System** – Businesses will be able to list upcoming events or accept customer bookings directly.  
- **📨 Messaging System** – Secure in-app messaging for direct communication between businesses and customers.  
- **📊 Business Insights Dashboard** – Analytics for business owners to track views, engagement, and customer interactions.  

## 👤 UX / User Stories  

To ensure a seamless experience, **Mind Your Own Business** is designed with the following user stories in mind:

### 🔹 As a Business Owner:
- I want to **create a business profile** so that I can showcase my services and contact details.  
- I want to **add promotions and special deals** to attract more customers.  
- I want to **edit or update my profile and promotions** easily.  
- I want my business to **be visible to users within a 10-mile radius** to target local customers.  
- I want to **see how many users view my business profile** to track engagement.  
- I want to **receive messages from interested customers** to increase sales.  

### 🔹 As a Customer:
- I want to **browse local businesses** so that I can find services near me.  
- I want to **filter businesses by category, location, and deals** to find relevant offers.  
- I want to **view business details and contact information** to connect with service providers.  
- I want to **read customer reviews and ratings** to make informed decisions.  
- I want to **create an account** so I can access more details about businesses.  
- I want to **save favorite businesses** for future reference.  

### 🔹 As a Platform Admin:
- I want to **manage user accounts** to ensure a secure and spam-free experience.  
- I want to **moderate business listings and promotions** to prevent misuse.  
- I want to **remove inactive or fraudulent accounts** to maintain platform integrity.  
- I want to **analyze platform usage data** to improve user experience and features.  

## Skeleton 
| Page | Desktop | Tablet | Mobile |
|------|---------|--------|--------|


## Technologies and tools used
+ **HTML5:** For the basic structure.
+ **CSS3:** For styling the website.
+ **JavaScript:** For dynamic content and interactivity
+ **Python:** 
+ **Flask:** 
+ **MongoDB:** 
+ **Google Maps API:** For fetching data.
+ **Balsamiq:** For creating wireframes.
+ **Visual Studio:** As a code editor.
+ **Github** For version control and collaboration.
+ **Gitpod** For cloud based development environment.  

## 🎨 Design Overview  

Mind Your Own Business is designed to provide a **user-friendly experience** for both business owners and customers. The platform features a **clean, intuitive interface** that makes it easy to browse businesses, post promotions, and connect with local services.

### 🖥️ Live Demo  
🔗 **Check out the live website:** [Mind Your Own Business](https://mind-your-own-business-5f784ff22ecb.herokuapp.com/)

### 🎯 Design Goals  
- **Simplicity** – A streamlined, hassle-free experience for users to find businesses and post promotions.  
- **Accessibility** – Fully responsive, ensuring smooth functionality across desktop, tablet, and mobile devices.  
- **Local Focus** – A location-based approach to show businesses and deals within a **10-mile radius** of the user.  
- **Authentication** – Secure login system for businesses to manage profiles and customers to engage with listings.  

### 📌 UI & UX Features  
- **👤 User-Friendly Navigation** – A simple, intuitive interface for easy browsing and interaction.  
- **🌍 Location-Based Listings** – Businesses and promotions are tailored to local customers.  
- **🎨 Responsive & Modern Design** – Built with **Materialize** for a clean, professional look.  
- **🔒 Secure Authentication** – Users must register to access full business profiles and engage with owners.  

## ✅ Testing  

### 🛠️ Functional Testing  

| Action | Expected Behaviour | Pass/Fail |
|--------|--------------------|-----------|
| User registers a new account | Account is created, and the user is redirected to their profile/dashboard | ✅ Pass |
| User logs in with valid credentials | User is successfully authenticated and redirected to the homepage | ✅ Pass |
| User logs in with incorrect credentials | Error message is displayed, and login is not allowed | ✅ Pass |
| Business owner creates a profile | Business profile is saved and visible on the platform | ✅ Pass |
| User adds a promotion | Promotion is saved and displayed under the business profile | ✅ Pass |
| User tries to access a business profile without logging in | Access is restricted, and login prompt is displayed | ✅ Pass |
| Search function is used | Businesses matching the search criteria are displayed | ✅ Pass |
| Promotions are displayed on the homepage | Active promotions are shown to all users | ✅ Pass |
| Logged-in user views a business profile | Full business details, including promotions, are visible | ✅ Pass |
| Non-logged-in user views promotions | Promotions are visible, but full business details require login | ✅ Pass |
| Business owner edits their profile | Changes are saved and updated on the platform | ✅ Pass |
| Business owner deletes their profile | Profile is removed from the system | ✅ Pass |
| User logs out | Session is cleared, and user is redirected to the homepage | ✅ Pass |


### HTML Test 
![w3c-html-test]()

### CSS testing
![w3c-css-testing]()

### Testing with JSLint
![incorrent-answer]()

## Deployment
1. **Design the Website on GitPod**:
   - Open GitPod and create a new workspace.
   - Design and develop your website within the GitPod environment.

2. **Push the Website to GitHub**:
   - Initialize a Git repository in your GitPod workspace:
     ```sh
     git init
     ```
   - Add all the project files:
     ```sh
     git add .
     ```
   - Commit the changes with a meaningful message:
     ```sh
     git commit -m "Initial commit"
     ```
   - Add your GitHub repository as a remote:
     ```sh
     git remote add origin <your-github-repo-url>
     ```
   - Push the changes to GitHub:
     ```sh
     git push -u origin main
     ```
## Cloning this repository

1. Open your prefered terminal.

2. Navigate to the directory where you want the cloned directory to be added.

3. Run the following command 
```sh
git clone https://github.com/DeanoPHP/quizzy-msp2
```

4. After cloning, navigate into the directory
```sh
 cd your-repository-name
```

5. Now you can start working on the project on your local machine.

## Forking this repository
1. Go to the repository on GitHub.

2. In the top-right corner of the page, click the "Fork" button.

3. Once the repository has been forked, you will be taken to your copy of the repository in your GitHub account.

4. Clone your forked repository to your local machine:
```sh
git clone https://github.com/DeanoPHP/quizzy-msp2
```

5. Navigate to the cloned directory
```sh
  cd your-repository-name
```

6. You can now make changes to your fork and submit pull requests to the original repository.

## Deployment Steps
<hr>

**Deploy to GitHub Pages**:
   - Go to your GitHub repository on GitHub.
   - Navigate to the repository settings.
   - Scroll down to the "GitHub Pages" section.
   - Under "Source", select the branch you want to deploy (usually `main` or `gh-pages`).
   - Click "Save".

Your website should now be live on GitHub Pages. You can access it via the URL provided in the GitHub Pages section of your repository settings.

# Credits and Acknowledgments
I would like to express my heartfelt gratitude to my mentor for his invaluable guidance and advice throughout this project.
Additionally, I extend my sincere thanks all my tutors for their exceptional teaching and encouragement. Your dedication and expertise have greatly contributed to my learning journey, Thank you.