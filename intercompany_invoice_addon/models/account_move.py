import base64
import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _inter_company_prepare_invoice_data(self, invoice_type):
        res = super()._inter_company_prepare_invoice_data(invoice_type)

        template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)

        if template:
            report_name = template._render_field('report_name', [self.id])[self.id]

            report = template.report_template
            report_service = report.report_name

            if report.report_type in ['qweb-html', 'qweb-pdf']:
                result, format = report.with_context(lang=self.partner_id.lang)._render_qweb_pdf([self.id])

                result = base64.b64encode(result)

                if not report_name:
                    report_name = 'report.' + report_service
                ext = "." + format

                if not report_name.endswith(ext):
                    report_name += ext

                invoice_attachment = self.env['ir.attachment'].create({
                    'name': report_name,
                    'res_model': 'account.move',
                    'datas': result,
                    'type': 'binary',
                })

                res['attachment_ids'] = [(4, invoice_attachment.id)]

        else:
            _logger.warning(_("No invoice mail template defined"))

        return res
