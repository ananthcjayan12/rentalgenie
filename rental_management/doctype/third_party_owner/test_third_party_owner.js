QUnit.module('Third Party Owner');

QUnit.test("test: Third Party Owner", function (assert) {
	let done = assert.async();

	// number of assertions
	assert.expect(1);

	frappe.run_serially('Third Party Owner', [
		// insert a new Third Party Owner
		() => frappe.tests.make_doctype('Third Party Owner', [
			// values to be set
			{owner_name: 'Test Owner'},
			{phone: '+919876543210'},
			{email: 'test@example.com'},
			{default_commission_rate: 50}
		]),
		() => {
			assert.equal(cur_frm.doc.owner_name, 'Test Owner');
		},
		() => done()
	]);

});
