import nextcord
from nextcord.ext import commands
from func.image import bytes_to_data_uri, bytes_read_qrcode
from func.sendSlip import sendSlip, sendSlipV2
import json

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.slash_command(name="checkslip", description="ตรวจสอบสลิปธนาคาร")
async def checkslip(interaction: nextcord.Interaction, file: nextcord.Attachment):
    await interaction.response.defer()
    
    if not file.content_type.startswith("image/"):
        await interaction.followup.send("❌ กรุณาอัปโหลดไฟล์รูปภาพเท่านั้น")
        return
        
    try:
        img_bytes = await file.read()
        result = sendSlip(bytes_to_data_uri(img_bytes))

        if "message" in result and "data" in result:
            data = result["data"]
            sender = data.get("sender_bank_details", {})
            receiver = data.get("receiver_bank_details", {})

            embed = nextcord.Embed(
                title="🧾 ผลการตรวจสอบสลิป",
                description=f"💬 **ข้อความ:** {result['message']}",
                color=int(receiver.get("color", "#4e2e7f").replace("#", "0x"), 16)
            )

            embed.add_field(
                name="🏦 ผู้ส่ง",
                value=(
                    f"👤 ชื่อ: {data.get('sender_name','-')}\n"
                    f"🏦 ธนาคาร: {sender.get('name','-')} ({data.get('sender_bank','-')})\n"
                    f"💳 SWIFT: {sender.get('swift_code','-')}"
                ),
                inline=True
            )

            embed.add_field(
                name="🏦 ผู้รับ",
                value=(
                    f"👤 ชื่อ: {data.get('receiver_name','-')}\n"
                    f"🏦 ธนาคาร: {receiver.get('name','-')} ({data.get('receiver_bank','-')})\n"
                    f"💳 SWIFT: {receiver.get('swift_code','-')}"
                ),
                inline=True
            )

            embed.add_field(
                name="💰 รายละเอียดการโอน",
                value=(
                    f"🆔 หมายเลขอ้างอิง: {data.get('ref','-')}\n"
                    f"📅 วันที่: {data.get('date','-')}\n"
                    f"💵 จำนวนเงิน: {data.get('amount',0)} THB"
                ),
                inline=False
            )

            embed.add_field(
                name="📌 อ้างอิงเพิ่มเติม",
                value=(
                    f"Reference 1: {data.get('reference_1','-')}\n"
                    f"Reference 2: {data.get('reference_2','-')}\n"
                    f"Reference 3: {data.get('reference_3','-')}"
                ),
                inline=False
            )

            embed.set_footer(text="ตรวจสอบสลิปโดย Bot ของคุณ")
            embed.timestamp = nextcord.utils.utcnow()

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ ไม่สามารถตรวจสอบสลิปได้ โปรดลองอีกครั้ง")
    except Exception as e:
        print(f"Error in checkslip: {e}")
        await interaction.followup.send("❌ เกิดข้อผิดพลาดในการตรวจสอบสลิป")

@bot.slash_command(name="checkslip_qr", description="ตรวจสอบสลิปธนาคารจาก QR Code")
async def checkslip_qr(interaction: nextcord.Interaction, file: nextcord.Attachment, amount: int):
    await interaction.response.defer()
    
    if not file.content_type.startswith("image/"):
        await interaction.followup.send("❌ กรุณาอัปโหลดไฟล์รูปภาพเท่านั้น")
        return
        
    try:
        # โหลด config
        with open("openslipverify.json", "r") as f:
            config = json.load(f)
        token = config.get("token", "")
        
        if not token:
            await interaction.followup.send("❌ Token สำหรับตรวจสอบสลิปไม่ถูกตั้งค่า")
            return

        img_bytes = await file.read()
        qr_data = bytes_read_qrcode(img_bytes)
        
        if not qr_data:
            await interaction.followup.send("❌ ไม่พบ QR Code ในรูปภาพ")
            return

        result = sendSlipV2(qr_data, amount, token)

        if result.get("success") and "data" in result:
            data = result["data"]
            sender = data.get("sender", {})
            receiver = data.get("receiver", {})

            embed = nextcord.Embed(
                title="🧾 ผลการตรวจสอบสลิป (QR Code)",
                description=f"💬 **ข้อความ:** {result.get('statusMessage','-')}",
                color=0x4e2e7f
            )

            embed.add_field(
                name="🏦 ผู้ส่ง",
                value=(
                    f"👤 ชื่อ: {sender.get('displayName', '-')}\n"
                    f"🏦 ธนาคาร: {data.get('sendingBank','-')}\n"
                    f"💳 บัญชี: {sender.get('account', {}).get('value','-')}"
                ),
                inline=True
            )

            embed.add_field(
                name="🏦 ผู้รับ",
                value=(
                    f"👤 ชื่อ: {receiver.get('displayName', '-')}\n"
                    f"🏦 ธนาคาร: {data.get('receivingBank','-')}\n"
                    f"💳 บัญชี: {receiver.get('account', {}).get('value','-')}"
                ),
                inline=True
            )

            embed.add_field(
                name="💰 รายละเอียดการโอน",
                value=(
                    f"🆔 หมายเลขอ้างอิง: {data.get('transRef','-')}\n"
                    f"📅 วันที่/เวลา: {data.get('transDate','-')} {data.get('transTime','-')}\n"
                    f"💵 จำนวนเงิน: {data.get('amount',0)} THB"
                ),
                inline=False
            )

            embed.set_footer(text="ตรวจสอบสลิปโดย Bot ของคุณ")
            embed.timestamp = nextcord.utils.utcnow()

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ ไม่สามารถตรวจสอบสลิปได้ โปรดลองอีกครั้ง")
    except Exception as e:
        print(f"Error in checkslip_qr: {e}")
        await interaction.followup.send("❌ เกิดข้อผิดพลาดในการตรวจสอบสลิป")

# @bot.slash_command(name="verify_slip", description="ตรวจสอบสลิปด้วยหมายเลขอ้างอิงและจำนวนเงิน")
# async def verify_slip(interaction: nextcord.Interaction, reference_number: str, amount: str):
#     await interaction.response.defer()
    
#     try:
#         # โหลด config
#         with open("openslipverify.json", "r") as f:
#             config = json.load(f)
#         token = config.get("token", "")
        
#         if not token:
#             await interaction.followup.send("❌ Token สำหรับตรวจสอบสลิปไม่ถูกตั้งค่า")
#             return

#         result = sendSlipV2(reference_number, amount, token)

#         if result.get("success") and "data" in result:
#             data = result["data"]
#             sender = data.get("sender", {})
#             receiver = data.get("receiver", {})

#             embed = nextcord.Embed(
#                 title="🧾 ผลการตรวจสอบสลิป (Manual)",
#                 description=f"💬 **ข้อความ:** {result.get('statusMessage','-')}",
#                 color=0x00ff00
#             )

#             embed.add_field(
#                 name="🏦 ผู้ส่ง",
#                 value=(
#                     f"👤 ชื่อ: {sender.get('displayName', '-')}\n"
#                     f"🏦 ธนาคาร: {data.get('sendingBank','-')}\n"
#                     f"💳 บัญชี: {sender.get('account', {}).get('value','-')}"
#                 ),
#                 inline=True
#             )

#             embed.add_field(
#                 name="🏦 ผู้รับ",
#                 value=(
#                     f"👤 ชื่อ: {receiver.get('displayName', '-')}\n"
#                     f"🏦 ธนาคาร: {data.get('receivingBank','-')}\n"
#                     f"💳 บัญชี: {receiver.get('account', {}).get('value','-')}"
#                 ),
#                 inline=True
#             )

#             embed.add_field(
#                 name="💰 รายละเอียดการโอน",
#                 value=(
#                     f"🆔 หมายเลขอ้างอิง: {data.get('transRef','-')}\n"
#                     f"📅 วันที่/เวลา: {data.get('transDate','-')} {data.get('transTime','-')}\n"
#                     f"💵 จำนวนเงิน: {data.get('amount',0)} THB"
#                 ),
#                 inline=False
#             )

#             embed.set_footer(text="ตรวจสอบสลิปโดย Bot ของคุณ")
#             embed.timestamp = nextcord.utils.utcnow()

#             await interaction.followup.send(embed=embed)
#         else:
#             await interaction.followup.send("❌ ไม่สามารถตรวจสอบสลิปได้ โปรดลองอีกครั้ง")
#     except Exception as e:
#         print(f"Error in verify_slip: {e}")
#         await interaction.followup.send("❌ เกิดข้อผิดพลาดในการตรวจสอบสลิป")
