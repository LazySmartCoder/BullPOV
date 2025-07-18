def otp_verification_template(otp):
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
                            Hello,
                        </p>
                        <p style="font-size: 16px; line-height: 1.6;">
                            Your One-Time Password (OTP) for verification is:
                        </p>
                        <div class="otp-box" style="background-color: #000000; color: #ffffff; padding: 20px; font-size: 28px; text-align: center; letter-spacing: 5px; margin: 20px 0; border-radius: 8px;">
                            {}
                        </div>
                        <p style="font-size: 14px; color: #555;">
                            Please do not share it with anyone.
                        </p>
                        <p style="font-size: 14px; margin-top: 30px;">
                            If you did not request this, please ignore this email or contact our support.
                        </p>
                        <p style="margin-top: 40px;">
                            Regards,<br />
                            <strong>Team BullPOV</strong>
                        </p>
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
            '''.format(str(otp))

def password_recovery_template(email, otp):
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
                            Hello,
                        </p>
                        <p style="font-size: 16px; line-height: 1.6;">
                            Please <a href="https://bullpov.com/password-recovery-verification/{0}-{1}"></a> to recover your password.
                        </p>
                        <p style="font-size: 14px; color: #555;">
                            Please do not share it with anyone.
                        </p>
                        <p style="font-size: 14px; margin-top: 30px;">
                            If you did not request this, please ignore this email or contact our support.
                        </p>
                        <p style="margin-top: 40px;">
                            Regards,<br />
                            <strong>Team BullPOV</strong>
                        </p>
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
            '''.format(email, otp)

def normal_text_templates(text):
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
                            Hello,
                        </p>
                        <p style="font-size: 16px; line-height: 1.6;">
                            {}
                        </p>
                        <p style="margin-top: 40px;">
                            Regards,<br />
                            <strong>Team BullPOV</strong>
                        </p>
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
            '''.format(text)
