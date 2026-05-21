# 📄 OCR Invoice Comparison App - AWS Deployment Guide

## **For Your Friend - Step-by-Step Instructions**

### **What You Need:**
1. AWS Account (you have this ✓)
2. Computer with Windows/Mac/Linux
3. About 15-20 minutes

---

## **STEP 1: Install Required Software**

### **1.1 Install Python**
- Go to: https://www.python.org/downloads/
- Download **Python 3.11** or latest
- Run installer, **CHECK "Add Python to PATH"** ✓
- Click Install

### **1.2 Install AWS CLI**
Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:
```bash
pip install awsebcli
```

### **1.3 Configure AWS Credentials**
1. Go to AWS Console: https://aws.amazon.com/
2. Login to your account
3. Click your **name (top right) → My Security Credentials**
4. Click **Access Keys → Create New Access Key**
5. Copy the **Access Key ID** and **Secret Access Key**

Now in Command Prompt, run:
```bash
aws configure
```

It will ask:
- **AWS Access Key ID**: [Paste your Access Key ID]
- **AWS Secret Access Key**: [Paste your Secret Access Key]
- **Default region name**: `us-east-1`
- **Default output format**: `json`

✓ Done!

---

## **STEP 2: Deploy the App**

### **2.1 Extract the ZIP File**
- Extract `Prince-OCR-App.zip` to any folder
- Open Command Prompt
- Go to that folder:
```bash
cd C:\path\to\Prince-work
```

### **2.2 Initialize AWS Elastic Beanstalk**
Run this command (only first time):
```bash
eb init -p python-3.11 --region us-east-1
```

It will ask:
- **Application name**: Press Enter (keep default)
- **Would you like to set up SSH?**: Type `N` and press Enter

### **2.3 Create and Deploy**
```bash
eb create production
```

**Wait 5-10 minutes.** AWS is setting up your app, installing libraries, Tesseract, Poppler, etc.

### **2.4 Open Your Live App**
```bash
eb open
```

Your app is now LIVE! 🎉 You'll see the URL in your browser.

---

## **STEP 3: How to Use the App**

1. You'll see an upload page
2. Upload **Invoice 1 (PDF)**
3. Upload **Invoice 2 (PDF)**
4. Click **Compare**
5. You'll see if they're the same or different

---

## **STEP 4: If You Need to Update the App**

### **Make changes to files locally, then:**
```bash
eb deploy
```

Done! New version is live in 2-3 minutes.

---

## **STEP 5: Stop the App (Save Money)**

To pause your app (when not using):
```bash
eb pause
```

To restart:
```bash
eb resume
```

To delete completely:
```bash
eb terminate
```

---

## **💰 Cost Breakdown**

- **AWS Free Tier**: Free for 12 months
- **After 12 months**: ~$10-20/month (if kept running)
- **Estimate**: ✅ Cheaper than most SaaS

---

## **❓ Troubleshooting**

### **"AWS credentials not found"**
- Run `aws configure` again
- Make sure you copied credentials correctly

### **"eb command not found"**
- Run: `pip install awsebcli` again
- Restart Command Prompt

### **App creation takes too long (>15 min)**
- It's still loading, be patient
- Don't close the command prompt

### **"Poppler not found" error**
- This shouldn't happen - AWS auto-installs it
- If it does, contact support or try `eb terminate` and `eb create production` again

---

## **📞 Need Help?**

If something goes wrong:
1. Take a **screenshot** of the error
2. Share it with your developer (who gave you this ZIP)

---

## **✅ You're All Set!**

Your app is ready to use. Share the live URL from `eb open` with anyone who needs it!

**Questions? Contact your developer.**
