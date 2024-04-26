import logging

from odoo import fields, models, tools

from odoo.addons.queue_job.exception import NothingToDoJob

_logger = logging.getLogger(__name__)
EXTERNAL_FIELD = "mirakl_id"
SYNC_DAT_FIELD = "sync_date"


class MiraklImporter(models.AbstractModel):
    _name = "mirakl.importer"
    _description = "import record from mirakl"

    def _build_dependencies(self, sale_channel, mirakl_record):
        return

    def _get_binding(self, sale_channel, external_id, binding_model):

        binding = (
            self.env[binding_model]
            .with_context(active_test=False)
            .search(
                [
                    ("mirakl_id", "=", tools.ustr(external_id)),
                    ("sale_channel_id", "=", sale_channel.channel_id.id),
                ],
                limit=2,
            )
        )

        if len(binding) > 1:
            _logger.warning("there are many records linked to the same mirakl record")
            binding = fields.first(binding)
        return binding

    def _get_importers(self, model):
        importers = {
            "res.partner": "mirakl.res.partner.importer",
            "sale.order": "mirakl.sale.order.importer",
        }
        return importers[model]

    def _build_dependency(
        self, sale_channel, mirakl_id, mirakl_data, binding_model, importer=None
    ):

        binding = self._get_binding(sale_channel, mirakl_id, binding_model)

        if not binding:
            if importer is None:
                importer_name = self._get_importers(binding_model)
                importer = self.env[importer_name]
            try:
                importer.create_or_update_record(
                    sale_channel, mirakl_id, mirakl_data, binding_model
                )
            except NothingToDoJob:
                _logger.info(
                    "Dependency import of %s(%s) has been ignored.",
                    binding_model,
                    mirakl_id,
                )

    def _map_data(self, mirakl_pydantic_object):
        return self.env["sale.channel.mirakl"]._map_to_odoo_record(
            mirakl_pydantic_object
        )

    # def _update_data(self, map_record, **kwargs):
    #     return map_record.values(**kwargs)
    #
    # def _update_record(self, binding, data):
    #     binding.with_context(connector_no_export=True).write(data)
    #     _logger.debug("%d updated from Mirakl %s", binding, self.mirakl_id)
    #
    #
    #
    # def _create_odoo_record(self, data, binding_model):
    #     model = self.env[binding_model].with_context(connector_no_export=True)
    #     binding = model.create(data)
    #     _logger.debug("%d created from Mirakl %s", binding, self.mirakl_id)
    #     return binding

    def attach_record(
        self, external_id, binding, binding_model
    ):  # from odoo.addons.connector.components.binder.py
        """Create the link between an external ID and an Odoo ID

        :param external_id: external id to bind
        :param binding: Odoo record to bind
        :type binding: int
        """
        # Prevent False, None, or "", but not 0
        assert (
            external_id or external_id == 0
        ) and binding, "external_id or binding missing, " "got: %s, %s" % (
            external_id,
            binding,
        )
        # avoid to trigger the export when we modify the `external_id`
        now_fmt = fields.Datetime.now()
        if isinstance(binding, models.BaseModel):
            binding.ensure_one()
        else:
            binding = self.env[binding_model].browse(binding)
        binding.with_context(connector_no_export=True).write(
            {
                EXTERNAL_FIELD: tools.ustr(external_id),
                SYNC_DAT_FIELD: now_fmt,
            }
        )

    def _after_import(self, binding):
        return

    def create_or_update_record(
        self, sale_channel, mirakl_id, mirakl_record, binding_model
    ):
        """

        :param mirakl_id: identifier of the record on Mirakl
        :param mirakl_data: data of the record on Mirakl
        """
        if not mirakl_id:
            mirakl_id = sale_channel._generate_hash_key(mirakl_record)

        binding = self._get_binding(sale_channel, mirakl_id, binding_model)
        self._build_dependencies(sale_channel, mirakl_record)

        map_record = self._map_data(mirakl_record)

        if binding:
            record = self._update_data(map_record)
            self._update_record(binding, record)
        else:

            binding = self._create_odoo_record(map_record, binding_model)

        self.attach_record(mirakl_id, binding, binding_model)
        self._after_import(binding)