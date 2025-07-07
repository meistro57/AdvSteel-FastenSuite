# FastenSuite Development Roadmap

The included study guides outline best practices for working with the Advance Steel `AstorBase` database. Based on those recommendations this project will evolve with the following milestones:

1. **Database safety** – provide a simple way to create versioned backups before any edit. This is implemented via the `/backup` endpoint and the `backup_db.py` helper.
2. **Data exchange utilities** – large bolt tables are often prepared in Excel/CSV as suggested in the study docs. The new `export_csv.py` script allows dumping any table directly to CSV for easier editing.
3. **Integrity checks** – custom bolts must keep foreign keys consistent. The `integrity_check.py` tool verifies that each `SetBolts.BoltDefID` has a matching entry in `BoltDefinition`.

4. **Row management** – tables can now have individual rows added or removed via new API endpoints. Validation ensures consistent columns when saving.

Future work will focus on inline validation, user roles and portable deployment so engineers can safely manage bolt libraries across versions.

