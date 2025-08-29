# POC Report

Date: 2025-08-28T16:47:03
Category: STATUS_SHIPPING
Validation cutoff: 2025-07-10

Patch summary:
- added keywords: ['name', 'company', 'email']
- instruction changed: True

Baseline metrics:
- keyword_accuracy: 0.075
- rougeL_templ_vs_human: 0.140

After patch metrics:
- keyword_accuracy: 0.178
- rougeL_templ_vs_human: 0.122

Best improved example:

- ROUGE-L before: 0.049
- ROUGE-L after: 0.100
- correct_cat: STATUS_RETURN | pred before → after: HOW_TO_RETURN → STATUS_SHIPPING
- incoming: Sure! Here’s the sanitized version of the email content:  ---  Hi [NAME],  Can I check on the status of this return, please.  [NAME]  On Fri, 13 Jun 2025 at 10:14, <[EMAIL]> wrote:  > Hi [NAME]! > > A...
- templated BEFORE: Hello! Thanks for your message. Handle return inquiries as follows:

• Standard Process:
 - Return label in package
 - Place label on parcel exterior
 - No additional attachments or website registrati...
- templated AFTER: Hello! Thanks for your message. Handle shipping status inquiries as follows and choose only the relevant and most fitting instructions:

• Delivery delays or no tracking updates:
  - Inform the custom...
- human: Hello, David,  Thanks for getting in touch! The return has not been registered and you will receive a payment within 4 banking days ...

Patch file: ../outputs\patches\patch_20250828_164703.json
Patched knowledge: ../outputs\knowledge_versions\knowledge_20250828_164703.json
