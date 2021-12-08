from odoo import _, fields, models
from odoo.exceptions import UserError


class CopyGlobalLeaves(models.TransientModel):
    _name = "resource_calendar_ux.copy_global_leaves"
    _description = "Copy Global Leaves"

    src_calendar_id = fields.Many2one(
        "resource.calendar",
        string="Source Calendar",
    )

    dest_calendar_ids = fields.Many2many(
        "resource.calendar",
        string="Destination Calendars",
    )

    def action_copy(self):
        self.ensure_one()
        if not self.src_calendar_id:
            raise UserError(_("Please select a source calendar."))

        if not self.src_calendar_id.global_leave_ids:
            raise UserError(_("The source calendar has no global leaves."))

        if not self.dest_calendar_ids:
            raise UserError(_("Please select at least one destination calendar."))

        candidate_leave_ids = self.src_calendar_id.global_leave_ids.filtered(
            lambda l: l.date_to >= fields.Datetime.now()
        )

        if not candidate_leave_ids:
            raise UserError(
                _(
                    "No global leaves found in the source calendar that end in"
                    " the future!"
                )
            )

        for dest_calendar in self.dest_calendar_ids:
            for global_leave in candidate_leave_ids:
                if not dest_calendar.global_leave_ids.filtered(
                    lambda x: x.date_from == global_leave.date_from
                    and x.date_to == global_leave.date_to
                ):
                    global_leave.copy(
                        {
                            "name": global_leave.name,
                            "calendar_id": dest_calendar.id,
                            "date_from": global_leave.date_from,
                            "date_to": global_leave.date_to,
                        }
                    )
