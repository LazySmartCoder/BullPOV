def otp_verification_template(name, otp):
    return '''
            <!DOCTYPE html>
            <html lang="en">

            <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>OTP Email</title>
            <style>
                /* Responsive styling for mobile */
                @media only screen and (max-width: 600px) {{
                .container {{
                    padding: 20px !important;
                }}

                .otp-box {{
                    font-size: 24px !important;
                    padding: 15px !important;
                }}
                }}
            </style>
            </head>

            <body style="margin: 0; padding: 0; background-color: #ffffff; font-family: Arial, sans-serif; color: #000000;">
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                <td align="center" style="background-color: #000000; padding: 20px;">
                    <h1 style="color: #ffffff; margin: 0;">BullPOV</h1>
                </td>
                </tr>
                <tr>
                <td>
                    <table align="center" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                    <tr>
                        <td class="container" style="padding: 40px;">
                        <p style="font-size: 18px; line-height: 1.6;">
                            Namaste {}!
                        </p>
                        <p style="font-size: 16px; line-height: 1.6;">
                            Welcome to BullPOV!
                        To complete your registration, please verify your email by entering the OTP below:
                        </p>
                        <div class="otp-box" style="background-color: #000000; color: #ffffff; padding: 20px; font-size: 28px; text-align: center; letter-spacing: 5px; margin: 20px 0; border-radius: 8px;">
                            {}
                        </div>
                        <p style="font-size: 14px; color: #555;">
                            This code is valid for only 10 minutes.
                            Please do not share it with anyone.
                            Thanks for joining us!
                        </p>
                        <p style="font-size: 14px; margin-top: 30px;">
                            If you didn’t sign up on our platform, you can safely ignore this email.
                        </p>
                        <p style="margin-top: 40px;">
                            Regards,<br />
                            <strong>Team BullPOV</strong>
                        </p>
                        <p>Please do not reply to this email. For any queries or assistance, feel free to contact us at support@bullpov.com</p>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="background-color: #f2f2f2; padding: 20px; font-size: 12px; color: #888;">
                        &copy; 2025 BullPOV. All rights reserved.
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>
            </table>
            </body>

            </html>
            '''.format(name, str(otp))

def normal_text_templates(name, text):
    return '''
            <!DOCTYPE html>
            <html lang="en">

            <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>OTP Email</title>
            <style>
                /* Responsive styling for mobile */
                @media only screen and (max-width: 600px) {{
                .container {{
                    padding: 20px !important;
                }}

                .otp-box {{
                    font-size: 24px !important;
                    padding: 15px !important;
                }}
                }}
            </style>
            </head>

            <body style="margin: 0; padding: 0; background-color: #ffffff; font-family: Arial, sans-serif; color: #000000;">
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                <td align="center" style="background-color: #000000; padding: 20px;">
                    <h1 style="color: #ffffff; margin: 0;">BullPOV</h1>
                </td>
                </tr>
                <tr>
                <td>
                    <table align="center" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                    <tr>
                        <td class="container" style="padding: 40px;">
                        <p style="font-size: 18px; line-height: 1.6;">
                            Namaste {}
                        </p>
                        <p style="font-size: 16px; line-height: 1.6;">
                            {}
                        </p>
                        <p style="margin-top: 40px;">
                            Regards,<br />
                            <strong>Team BullPOV</strong>
                        </p>
                        <p>Please do not reply to this email. For any queries or assistance, feel free to contact us at support@bullpov.com</p>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="background-color: #f2f2f2; padding: 20px; font-size: 12px; color: #888;">
                        &copy; 2025 BullPOV. All rights reserved.
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>
            </table>
            </body>

            </html>
            '''.format(name, text)
