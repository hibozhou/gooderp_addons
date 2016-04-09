# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
from openerp.exceptions import except_orm

class test_report(TransactionCase):
    def test_bank_report(self):
        ''' 测试银行对账单报表 '''
        self.env['go.live.order'].create({'bank_id': self.env.ref('core.comm').id, 'balance':20.0})
        # _compute_balance，name == '期初余额'
        go_live = self.env['bank.statements.report.wizard'].create({'bank_id': self.env.ref('core.comm').id,
                                                                    'from_date': '2016-11-01', 'to_date': '2016-11-03'})
        go_live.confirm_bank_statements()
        live = self.env['bank.statements.report'].search([('name', '=', '期初余额')])
        self.assertNotEqual(str(live.balance), 'zxy11')
        # 执行向导
        statement = self.env['bank.statements.report.wizard'].create(
                    {'bank_id': self.env.ref('money.money_order_line_2').bank_id.id,
                    'from_date': '2016-11-01',
                    'to_date': '2016-11-03'})
        statement_other = self.env['bank.statements.report.wizard'].create(
                    {'bank_id': self.env.ref('money.bank_report_other_get_1').bank_id.id,
                    'from_date': '2016-11-01',
                    'to_date': '2016-11-03'})
        last_balance = self.env.ref('core.comm').balance
        self.env.ref('money.bank_report_other_get_1').other_money_done()
        self.assertEqual(self.env.ref('core.comm').balance, last_balance + 2000.0)
        # 执行_compute_balance
        statement_other.confirm_bank_statements()
        statement_money = self.env['bank.statements.report'].search([('name', '=', 'OTHER_GET/20160001')])
        self.assertNotEqual(str(statement_money.balance), 'zxy')

        statement_transfer_out = self.env['bank.statements.report.wizard'].create(
                    {'bank_id': self.env.ref('money.transfer_order_line').out_bank_id.id,
                    'from_date': '2016-11-01',
                    'to_date': '2016-11-03'})
        statement_transfer_in = self.env['bank.statements.report.wizard'].create(
                    {'bank_id': self.env.ref('money.transfer_order_line').in_bank_id.id,
                    'from_date': '2016-11-01',
                    'to_date': '2016-11-03'})
        self.env.ref('money.bank_report_transfer_1').money_transfer_done()
        # 输出报表
        statement.confirm_bank_statements()
        statement_transfer_out.confirm_bank_statements()
        statement_transfer_in.confirm_bank_statements()
        # 测试现金银行对账单方法中的'结束日期不能小于开始日期！'
        statement_date_error = self.env['bank.statements.report.wizard'].create(
                    {'bank_id': self.env.ref('money.money_order_line_2').bank_id.id,
                    'from_date': '2016-11-03',
                    'to_date': '2016-11-02'})
        with self.assertRaises(except_orm):
            statement_date_error.confirm_bank_statements()
        # 测试现金银行对账单方法中的from_date的默认值是否是公司启用日期
        statement_date = self.env['bank.statements.report.wizard'].create(
                    {'bank_id': self.env.ref('money.money_order_line_2').bank_id.id,
                     'to_date': '2016-11-03'})
        self.assertEqual(statement_date.from_date, self.env.user.company_id.start_date)
        # 查看对账单明细
        statement_money = self.env['bank.statements.report'].search([])
        for money in statement_money:
            money.find_source_order()

    def test_other_money_report(self):
        ''' 测试其他收支单明细表'''
        # 执行向导
        statement = self.env['other.money.statements.report.wizard'].create(
                    {'from_date': '2016-11-01',
                    'to_date': '2016-11-03'})
        # 输出报表
        statement.confirm_other_money_statements()
        # 测试其他收支单明细表方法中的'结束日期不能小于开始日期！'
        statement_error_date = self.env['other.money.statements.report.wizard'].create(
                    {'from_date': '2016-11-03',
                     'to_date': '2016-11-01'})
        # 输出报表，执行if
        with self.assertRaises(except_orm):
            statement_error_date.confirm_other_money_statements()
        # 测试其他收支单明细表方法中的from_date的默认值
        statement_date = self.env['other.money.statements.report.wizard'].create(
                    {'to_date': '2016-11-03'})
        # 判断from_date的值是否是公司启用日期
        self.assertEqual(statement_date.from_date, self.env.user.company_id.start_date)

    def test_partner_statements_report(self):
        ''' 测试业务伙伴对账单报表'''
        statement = self.env['partner.statements.report.wizard'].create(
                    {'partner_id': self.env.ref('core.yixun').id,
                     'from_date': '2016-01-01',
                     'to_date': '2016-03-10'})
        statement_customer = self.env['partner.statements.report.wizard'].create(
                    {'partner_id': self.env.ref('core.jd').id,
                     'from_date': '2016-01-01',
                     'to_date': '2016-03-10'}).with_context({'default_customer': True})
        # onchange_from_date 业务伙伴先改为供应商，再改为客户
        statement.onchange_from_date()
        statement_customer.onchange_from_date()