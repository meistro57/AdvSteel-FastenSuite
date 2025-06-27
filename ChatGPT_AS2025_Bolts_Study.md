# Advance Steel Bolt Database Schema and Custom Bolt Insertion Guide

## Overview

Autodesk Advance Steel stores bolt, nut, and washer configurations in a SQL Server database (`AstorBase.mdf`). Understanding the schema of this database is crucial for safely adding or editing bolt sizes outside the Management Tools UI. Multiple tables in AstorBase are involved in defining a “bolt assembly” (a bolt plus its associated nuts/washers). Each table has a specific role, and they are linked by foreign keys to maintain data integrity. This guide provides a detailed breakdown of the key tables (e.g. **BoltDefinition**, **SetBolts**, **Standard**, **SetOfBolts**, etc.), their relationships, and a step-by-step procedure to insert a new custom bolt assembly (for example, an **M16 × 70** bolt to a DIN standard). We also cover best practices for maintaining database integrity (managing IDs, avoiding constraint violations) and highlight any gotchas or undocumented behaviors. Always **backup the database** before making changes and follow these guidelines to avoid corrupting your Advance Steel configuration.

## Key Tables for Bolt Definitions in AstorBase

Advance Steel’s AstorBase database uses several interrelated tables to define bolts and their assemblies. A new bolt assembly will typically require new records in **multiple tables**. (In fact, a single new bolt type with a full range of lengths can involve **hundreds of entries across the various tables**.) Below we describe the purpose of each key table and its structure, focusing on bolts:

* **BoltDefinition** (sometimes referred to as `ScrewNew` in the database): This table stores the *base properties of each bolt type*. Each record in BoltDefinition represents a unique bolt **type** (by diameter, thread, grade, and standard) – essentially the bolt *family* without specifying a length. Key fields include:

  * **ID** – Primary key identifier for the bolt type (unique int).
  * **StandardId** – Foreign key to the **Standard** table, indicating which bolt standard/norm this bolt follows. For example, a DIN 6914 bolt would link to a DIN standard entry in Standard.
  * **StrengthClassId** – Foreign key to a **StrengthClass** table that defines the bolt grade or strength (e.g. 4.6, 8.8, 10.9, ASTM A325, etc.). This ensures the mechanical grade is recorded.
  * **Diameter** – Nominal bolt diameter (in mm for metric, or inches for imperial) used for matching nuts and holes.
  * **Name** or **Designation** – Descriptive name of the bolt (often including diameter, length, standard, grade), used for identification in the UI. For example, “Bolt M16-70 DIN 6914”.
  * **Head geometry fields** – Various columns for physical dimensions of the bolt head (e.g. head diameter across flats, head thickness, wrench size, number of flats or corners if needed). These correspond to values entered on the “Bolts” tab in Management Tools (head width, thickness, etc.). The bolt’s thread length or thread type may also be specified here or derived from standards.
  * **AuthorId** – Foreign key to the **Authors** table, indicating who created or provided this entry. Built-in entries are tagged with Autodesk/Graitec, while custom entries should use a “User” or company author entry. (You can use an existing Author ID for custom content or insert a new author in the Authors table for tracking.)
  * *Other fields:* There may be additional fields like default coating, thread designation, material, etc., depending on Advance Steel’s schema. Use existing entries as a template to ensure all required fields are filled.

* **SetBolts**: This table contains the **specific bolt length entries** for each bolt type. In Advance Steel, each available length of a given bolt type is a separate record in SetBolts. In other words, once a bolt has a definition in BoltDefinition, every usable length (e.g. 50 mm, 60 mm, 70 mm, etc.) must appear as a row in SetBolts. Key fields include:

  * **ID** – Primary key for the bolt length entry.
  * **BoltDefId** – Foreign key linking to the BoltDefinition.ID of the bolt type. This associates the length with its parent bolt type.
  * **Length** – The bolt length (typically in mm). Each length your application should support (e.g. 70 mm) needs a record.
  * **PartName** – A name or designation for this specific bolt length, used in BOMs/labels. Often this is similar to the bolt name plus the length (e.g. “M16x70”).
  * **Weight** – The weight of one bolt of this size (usually in kilograms or another consistent unit). Ensure to calculate or copy this from a similar entry (the weight is used for BOM weight calculations).
  * **Additional fields:** Possibly a part number or external code, stock length flags, or threading info. For example, some standards might indicate if a length is fully threaded or partially threaded via a flag or separate table. Check if fields like “ThreadLength” exist or if thread lengths are auto-calculated. Fill out any required fields by referencing how other bolts are entered.

* **Standard**: Despite the name, this table in AstorBase defines each *bolt standard or norm* and certain default behaviors for bolts under that standard. Each entry in Standard represents a category like “DIN 931” or “ASTM A325” or “ISO 4014,” etc.. Key fields likely include:

  * **ID** – Primary key for the standard entry.
  * **Name** – Standard code or identifier (e.g. “DIN 6914”).
  * **RunName** – The display name of the standard as seen in the UI (often the same as Name or a more descriptive text). For example, the UI’s bolt standard dropdown shows “DIN 6914” which corresponds to this field.
  * **DefaultSet** – The default bolt assembly configuration for this standard. This field defines which assembly (from the Sets table, see below) bolts of this standard will use by default. For instance, many DIN/ISO standards might default to “Na2W” (meaning a nut and 2 washers) or “NaW” (nut and 1 washer) as the bolt assembly. Changing this value will change the default nut/washer set applied when you place a bolt of that standard (as one Autodesk forum user did by changing all “NaW” to “Na2W” in the Standard table to get two washers by default).
  * **Related fields:** The Standard table may also indicate other standard-specific settings, such as references to what nut and washer standards to use. In some cases, there are separate tables for nut standards (e.g. a **StandardNuts** table) and possibly washer standards. It’s possible that Standard entries have an associated nut standard via another table or field. For example, the DIN 6914 bolt standard typically uses DIN 6915 nuts and DIN 6916 washers – the database likely knows this mapping so that when you select a DIN 6914 bolt, the correct nut/washer dimensions are used. This mapping might be stored in **StandardNuts** or directly in **SetNutsBolts** (discussed below). Be aware of this relationship: if you introduce a completely new bolt standard, you may need to also define the corresponding nut and washer standards to avoid missing data.

* **Sets**: The Sets table defines the **bolt assembly configurations** (the combination of nuts and washers that make up a “bolt set”). Each entry in Sets is essentially a code for a particular arrangement of nut(s) and washer(s). Key fields:

  * **ID** – Primary key for the assembly set.
  * **SetCode** or **Name** – A short code for the assembly. For example: “N” (one nut, no washer), “NW” (nut + one washer), “Na2W” (nut + two washers), “2N2W” (double nut with two washers), etc. Advance Steel uses these codes in the bolt assembly dropdown.
  * **Description** – A human-readable description (e.g. “1 Nut + 2 Washers”). This helps identify the set in the Management Tools UI.
  * **Type/Usage** – Possibly a field indicating if this set is for bolts vs anchors (if shared). Standard sets like “Na2W” are typically predefined. You usually will not need to add new codes unless you have a non-standard assembly; instead you will use one of the existing codes. (If you do need a new assembly type, add it here and then define its nut/washer components in SetNutsBolts.)

* **SetOfBolts**: This is a linking table that **associates each bolt type with the assembly set(s) that are allowed** for it. In other words, SetOfBolts defines which bolt assemblies can be used with a given bolt (identified by its BoltDefinition). Each record typically links one BoltDefinition to one Set (assembly code):

  * **BoltDefId** – Foreign key to BoltDefinition.ID, identifying the bolt type.
  * **SetId** – Foreign key to Sets.ID, identifying an assembly configuration.
  * Together, these two fields form the relationship: e.g. Bolt type “M16 DIN 6914” may have SetId pointing to “Na2W” entry, meaning an M16 DIN 6914 bolt can be used with nut + 2 washers. If multiple assembly options are possible for a bolt type, it will have multiple records in SetOfBolts (one for each allowed Set). For example, you might allow both “Na2W” and “NaW” for a certain bolt, giving users a choice.
  * **Required fields:** Both foreign keys must be valid. There may not be additional data in this table beyond the relationship itself. Ensure that for any new BoltDefinition, you insert at least one SetOfBolts entry or the bolt will not appear in the Advance Steel UI (because the software won’t know what nut/washer set to use with it). Typically you will choose the standard’s default set or whichever is appropriate. (Most structural bolts use one nut and two washers by default, but confirm based on your standard.)

* **SetNutsBolts**: This table defines the **nut and washer details for each assembly set, standard, and diameter combination**. Essentially, SetNutsBolts tells Advance Steel *which specific nuts and washers (and their dimensions)* to use for a given bolt standard and assembly code. Each record might correspond to one diameter under a certain standard with a specific assembly. Key fields likely include:

  * **StandardId** – Foreign key to Standard.ID (the bolt’s standard). This ties the entry to a particular bolt norm (e.g. DIN, AISC, etc.).
  * **SetId** – Foreign key to Sets.ID (the assembly code, like N, NW, Na2W).
  * **Diameter** – The nominal diameter of the bolt for which this entry applies. This is probably a numeric field (in mm for metric bolts) that matches the BoltDefinition’s diameter. Together with StandardId and SetId, it identifies a unique scenario (e.g. “For DIN 6914 bolts of diameter 16 mm with assembly Na2W, use the following nut/washer dims…”).
  * **Nut dimensions** – Fields for nut properties. Likely the nut’s thickness and across-flats size (and possibly nut standard or code). For example, for M16 heavy-hex nut (DIN 6915), this table might have something like NutThickness \~ 13 mm, NutAcrossFlats \~ 24 mm. It may also explicitly store a **NutStandard** reference (linking to a StandardNuts table entry) or an ID for the nut part, depending on schema. If a **StandardNuts** table exists, there could be a StandardNutsId instead of raw dimensions, with StandardNutsId pointing to a table of nut types.
  * **Washer dimensions** – Fields for washer properties. Since many sets involve two washers, there could be fields for top and bottom washer thickness and diameter (or just one set if washers are identical). For example, a hardened washer (DIN 6916) for M16 might have WasherThickness \~ 4 mm and outer diameter \~ 34 mm. The table might have one record per diameter where both washers are assumed identical, or separate fields if two washers differ.
  * **Other fields:** There might be a *BoltProjection* or thread engagement length field for certain calculations (e.g. how much the bolt should protrude beyond the nut) – this could be defined per standard or assembly as well. If present, ensure it’s set (often a default like 2–3 threads protruding).
  * **Purpose:** The presence of the correct SetNutsBolts entry is essential for modeling and clash checking – Advance Steel uses these values to model the nut and washers and to ensure proper hole diameters and clearances. If you add a new bolt size that wasn’t in the standard before, you must confirm that SetNutsBolts has an entry for that diameter. Often, if the bolt standard already covered a range of diameters, the necessary nut/washer data is *already present* (e.g. DIN 6914 covers M12–M36, etc.). If you add a diameter outside the original range or a new standard, you’ll need to insert new records here with the correct nut/washer info. It’s usually easiest to copy an existing row for a similar diameter and just adjust the values if needed, to ensure consistency.

* **StrengthClass**: This table (if present) lists the **bolt strength grades/classes** and their properties. Examples of StrengthClass entries could be “8.8”, “10.9”, “A325”, etc. Fields might include an ID, a name (grade designation), and possibly mechanical properties like yield/tensile strength or a category (metric vs imperial). BoltDefinition likely references StrengthClass by ID to specify the bolt’s grade. If you are adding a bolt with a grade already in the system (e.g. 8.8), just use that existing StrengthClass ID. Only if you needed a completely new grade would you add here. Maintaining correct grade is important for documentation and bolt list outputs.

* **Authors**: The Authors table tracks the source of each data entry (to distinguish standard content from custom content). It has an ID and a Name. By default, Autodesk/Graitec entries might have Author like “Autodesk” or “AdvanceSteel” and custom entries could be “User”. For integrity, assign a proper AuthorId in BoltDefinition (and any other table that requires it) for new bolts. You can use the built-in “User” author ID (if exists, often there is one for user-added content) or create a new entry with your company/name. This helps keep track of custom additions.

* **AutoLength**: (Optional, but important for automatic bolt sizing) This table defines rules for **automatic bolt length selection**. Advance Steel can automatically choose a bolt length based on the grip (thickness of connected materials + washers/nuts) if the bolt type is enabled for auto-length. The AutoLength table typically contains many entries for each bolt type, mapping a grip range to a required bolt length. Key fields likely include:

  * **BoltDefId** – Foreign key to the BoltDefinition (which bolt type the rule applies to).
  * **GripMin** and **GripMax** – The range of total thickness (in mm) that this rule covers.
  * **Length** – The recommended bolt length for that grip range. This length should exist in the SetBolts table for the bolt.
  * By covering all possible grip values, the AutoLength table allows Advance Steel to pick, say, a 70 mm bolt if the connected plates + washers are, for example, 54 mm thick (because 54 mm falls into the range that maps to a 70 mm bolt). If you add a new bolt length or a new bolt type, you might want to add or update AutoLength entries so that the auto-selection feature knows about the new length. (If you skip this, the new bolt can still be used, but automatic length calculation might not consider it and could choose the next larger available length or none at all, forcing manual length selection.)
  * **Note:** The content of AutoLength can be quite extensive – often hundreds of entries per bolt type covering each incremental thickness. To create these, it may be easiest to use a spreadsheet or script. If your new bolt is just one additional length for an existing type, check if the existing AutoLength ranges need adjustment (for example, if you added a longer bolt, extend the last range). If you created a completely new bolt type, you’ll need to populate AutoLength for it (this can be done by copying a similar standard’s ranges and modifying as needed). AutoLength is not strictly required to simply *have* a bolt length in the database, but without it, “Auto” length mode in connections won’t know how to pick your new size.

**Relationships between tables:** All the above tables are linked via key fields to maintain consistency. The entity-relationship diagram below illustrates the main relationships:

&#x20;*Figure: Simplified schema of key bolt tables in AstorBase. Each **BoltDefinition** (bolt type) references a **Standard** (norm) and a **StrengthClass** (grade) and is attributed to an **Author**. Each BoltDefinition can have many entries in **SetBolts** (one per available length). BoltDefinition also links to allowed assembly **Sets** through **SetOfBolts** (many-to-many via SetOfBolts). Each **Standard** has a default assembly and corresponds to specific **nut/washer data** in **SetNutsBolts** for each diameter and set. (StandardNuts/washer tables are not shown for brevity.) The **AutoLength** table (not shown in diagram) links to BoltDefinition for automatic length selection rules.*

In summary, to add a new bolt properly, **all references must be consistent**: the StandardId and StrengthClassId in BoltDefinition must exist; the BoltDefId in SetBolts, SetOfBolts, and AutoLength must match the new BoltDefinition’s ID; SetId values must match an entry in Sets; and any StandardId/SetId/diameter combination used in SetNutsBolts should be covered. The database likely enforces some of these via foreign key constraints (e.g. you cannot add a SetOfBolts if the BoltDefId or SetId do not exist – the insert will fail). Even if constraints are not explicit, the application will behave incorrectly if these links are broken. Always ensure **no “orphan” records** are created (e.g. a SetBolts entry with a BoltDefId that doesn’t exist, or a BoltDefinition with a StandardId that isn’t in Standard). It’s wise to use SQL queries to double-check referential integrity after inserts (for example, check that every BoltID in BoltsCoating or SetBolts corresponds to a BoltDefinition ID).

## Procedure: Safely Inserting a New Bolt Assembly (Example: M16 × 70, DIN Standard)

Adding a new bolt assembly to Advance Steel via direct database manipulation involves inserting data into several tables in the correct order. This example will walk through adding an **M16 diameter, 70 mm length** bolt under a **DIN** standard (assuming a grade like 8.8 or 10.9). The same general steps apply for other sizes or standards. Adapt the steps as needed if you are introducing a completely new standard or grade.

**Before you begin:** Make sure **Advance Steel is closed** to prevent it from locking the database. **Back up the database files** (AstorBase.mdf and the corresponding .ldf log) to a safe location before any edits. You can copy the files from `C:\ProgramData\Autodesk\Advance Steel ####\Steel\Data\` to make a backup. It’s also recommended to use SQL Server Management Studio (SSMS) or an equivalent tool to connect to the LocalDB instance for running queries, or use your custom PyQt tool’s SQL interface carefully. In SSMS, attach the AstorBase.mdf database if it’s not already attached to your LocalDB. Once backed up and connected, proceed with the insertions:

1. **Determine or Insert the Standard:** Verify that the relevant bolt standard (norm) exists in the **Standard** table. For our example, we need the DIN standard for this bolt. Advance Steel has multiple DIN standards (e.g., DIN 931/933 for standard hex bolts, or DIN 6914 for high-strength structural bolts). Choose the appropriate one for your bolt. If it already exists, note its ID. If not, you must create a new entry. For example, if we needed a new standard “DIN 6914” and it wasn’t there, we would insert it:

   ```sql
   -- If DIN 6914 standard is not already present in Standard table:
   INSERT INTO [Standard] (Name, RunName, DefaultSet, ...) 
   VALUES ('DIN 6914', 'DIN 6914 High-strength bolt', 'Na2W', ...);
   ```

   *Replace* `'DIN 6914'` with the actual standard code/name required. The `DefaultSet` in this example is `'Na2W'` (1 Nut + 2 Washers) which is typical for structural bolts – adjust if needed. Additional fields (omitted as `...`) might include region or notes; fill as appropriate. If the standard is already present, skip this step (but make sure you are satisfied with its DefaultSet – you can change the default assembly for the standard if desired, as noted earlier).

2. **Ensure the Strength Class (Grade) Exists:** Identify the bolt grade. For instance, DIN 6914 bolts are usually property class 10.9. Check the **StrengthClass** (or similar) table for an entry “10.9”. If it exists, note its ID. If you needed a new grade, insert it accordingly (rare, since common grades are likely present). For example, if adding “ASTM A325” and it wasn’t there, you’d add it with its designation and maybe mechanical properties. In our M16 example, we’ll assume 10.9 exists and use its ID.

3. **Insert into BoltDefinition:** Now create a new bolt type entry in the **BoltDefinition** table. This defines the bolt’s core properties (diameter, grade, standard, etc.). Here you will reference the StandardId from step 1 and StrengthClassId from step 2. You also need to supply all the necessary geometric and naming data. For example:

   ```sql
   INSERT INTO [BoltDefinition] 
       (Name, StandardId, Diameter, StrengthClassId, AuthorId, HeadDiameter, HeadThickness, ThreadType, ...) 
   VALUES 
       ('Bolt M16-70 DIN 6914', <StandardID_for_DIN6914>, 16.0, <StrengthClassID_for_10.9>, <AuthorID_custom>, <HeadAcrossFlats>, <HeadHeight>, 'metric_coarse', ...);
   ```

   In this SQL:

   * **Name:** A descriptive name. It’s good practice to include the diameter, a representative length or “varied” if many lengths, the standard, and perhaps grade. Here we used “Bolt M16-70 DIN 6914”. (The length 70 in the name is optional; sometimes names omit the length if multiple lengths share one definition. You could also name it just "Bolt M16 DIN 6914" since length will vary. The UI might show “Diameter – length – standard” elsewhere anyway.)
   * **StandardId:** replace `<StandardID_for_DIN6914>` with the ID noted or inserted in step 1.
   * **Diameter:** 16.0 (for M16). Use the exact unit conventions as existing entries (likely mm for metric).
   * **StrengthClassId:** replace `<StrengthClassID_for_10.9>` with the ID from step 2.
   * **AuthorId:** replace `<AuthorID_custom>` with your chosen author ID. If you have an “Author” entry for custom entries (check the Authors table for something like “User” or your company’s name), use that ID. This is not just cosmetic – it can help during migration or identifying custom content.
   * **HeadAcrossFlats, HeadHeight:** specify the bolt head dimensions. For an M16 heavy hex structural bolt (DIN 6914), the across-flats (wrench size) is typically 24 mm and head thickness around 10 mm (for hex head). Use values from standards or measure an existing similar bolt entry: for example, if a DIN 931 M16 exists, it might have 24 mm across flats and \~10 mm high head. Insert those as `<HeadAcrossFlats>` and `<HeadHeight>`. If your bolt has a different head (e.g., countersunk or other shape), provide the appropriate geometry fields (e.g., head diameter, angle, etc.).
   * **ThreadType or ThreadDesignation:** If there’s a field for thread type, you might put ‘M16’ or an indicator of coarse thread. Many metric bolts use standard coarse thread so this may not need special entry, but ensure any required thread info (like thread length or a flag for fully threaded) is handled. Some databases have a separate way to compute thread length (possibly via the Tools table or formula). If in doubt, check if similar bolts have a ThreadLength field or if they rely on AutoLength to cover thread engagement.
   * **Additional fields:** The BoltDefinition table may require values for default hole type or coating or other flags (for example, a boolean if this bolt is available for automatic selection). Again, refer to an existing bolt of similar type. If the UI’s “Parameters” tab or others correspond to fields, fill them. Common ones might include: material (though usually grade covers that), coating (maybe a separate table BoltsCoating can be left default), and possibly a field linking to a specific nut type (often indirectly via standard). Fill all **non-nullable fields** to avoid errors.

   Once executed, this INSERT will create a new BoltDefinition. Note the **new BoltDefinition ID** (if using SSMS, you can use `SCOPE_IDENTITY()` or just SELECT it afterward). We will need it for subsequent steps.

4. **Insert into SetBolts (Length entries):** Now add the specific length(s) for the bolt. In our case, we want to add the 70 mm length. Each length is one row in **SetBolts** with a reference to the BoltDefinition. Assuming we got the new BoltDefinition ID (let’s call it `<NewBoltDefID>`), we insert a SetBolts row:

   ```sql
   INSERT INTO [SetBolts] 
       (BoltDefId, Length, Weight, PartName, ...) 
   VALUES 
       (<NewBoltDefID>, 70.0, 0.138, 'M16x70', ...);
   ```

   Here:

   * **BoltDefId:** put the ID of the new bolt type from step 3. This links the length to that bolt.
   * **Length:** 70.0 (millimeters). Use a decimal if the field is float, or integer if it’s int – match existing entries’ format.
   * **Weight:** approximate weight of one bolt of this size. If you don’t have an exact value, you can estimate or copy from a similar entry. For example, a black (plain) M16×70 Grade 10.9 bolt might weigh around 0.13–0.14 kg. We used 0.138 as a placeholder. It’s best to be accurate for BOM weight totals. If you have another length of M16 in the DB (say M16×60 and M16×80), you can interpolate or find a weight-per-unit-length. Alternatively, leave it zero or a dummy value initially and update later via the Management Tools UI (not ideal for final, but okay to get it in).
   * **PartName:** a short name for this bolt length. “M16x70” is typical. Some standards might include the grade or norm in the part name, depending on how BOM templates are set up. Check how existing ones are. Often, BOM part names are just diameter × length (and the drawing bill of materials may list the standard separately). So “M16x70” is likely fine here.
   * **Other fields:** If the SetBolts table has fields like “Material” or “ThreadLength” or other flags, set them appropriately. Possibly it doesn’t, since those are usually at the definition level, but just be thorough. In some databases, each length might have an associated part number or model role – again, use an existing row as a guide.

   If you plan to add multiple lengths (say a whole range of M16 lengths), you would insert each one into SetBolts with the same BoltDefId. In this example, we’re just adding 70 mm.

5. **Link the Bolt to an Assembly Set (SetOfBolts):** Next, ensure the new bolt type can actually be used with at least one nut/washer configuration. In the **SetOfBolts** table, insert a record linking your `<NewBoltDefID>` to the appropriate assembly **SetId**. We will use the default from our standard, which we set as “Na2W” (nut + 2 washers). We need to find the ID of “Na2W” in the **Sets** table. (Common assembly codes like “N” or “Na2W” should already be present in Sets. You can `SELECT * FROM Sets` to find it, or query `WHERE Code='Na2W'`.) Suppose the SetId for “Na2W” is X. Insert:

   ```sql
   INSERT INTO [SetOfBolts] (BoltDefId, SetId) 
   VALUES (<NewBoltDefID>, <SetID_for_Na2W>);
   ```

   If you want the bolt to be available with multiple configurations, you can insert multiple rows here (one for each SetId). However, typically one standard has one preferred assembly. To stick with our example, one entry for Na2W is enough. *(Optional:* If you wanted to allow a single washer variant “NaW” as well, you’d also insert that. The first one in the database might be treated as default if not overridden elsewhere, but since Standard.DefaultSet is Na2W, Advance Steel will default to Na2W anyway).)

6. **Nut and Washer Data (SetNutsBolts):** This step is **critical** to avoid missing components. After adding the bolt and linking the assembly, you must ensure that the nut and washer dimensions for this bolt’s standard, diameter, and assembly are defined in **SetNutsBolts**. For our **DIN 6914, M16, Na2W** example, we need to verify if an entry already exists in SetNutsBolts. Many DIN standards cover a range of diameters, so if M16 was already part of that standard’s range, the row might already be there. For instance, if DIN 6914 bolts from M12 up to M36 are present by default, then SetNutsBolts probably has M16 data for Na2W. You can check with a query like:

   ```sql
   SELECT * FROM SetNutsBolts 
   WHERE StandardId = <StandardID_for_DIN6914> AND SetId = <SetID_for_Na2W> AND Diameter = 16.0;
   ```

   If this returns a row, inspect if the values (nut height, washer thickness, etc.) look correct. If a row is **absent**, you must insert one. Using known values for heavy hex M16 hardware: DIN 6915 nut (M16) is 0.8×d high (≈12.8 mm) and 24 mm across flats; DIN 6916 washer is 4 mm thick and 34 mm outer diameter. These are example values – please confirm actual standard data. The insert might look like:

   ```sql
   INSERT INTO [SetNutsBolts] 
       (StandardId, SetId, Diameter, NutThickness, NutWidthAcrossFlats, WasherThickness, WasherOuterDia, ...) 
   VALUES 
       (<StandardID_for_DIN6914>, <SetID_for_Na2W>, 16.0, 13.0, 24.0, 4.0, 34.0, ...);
   ```

   Fill in the `...` with any other required fields, such as a second washer thickness if needed (perhaps the table could have separate TopWasherThickness/BottomWasherThickness – but likely both washers are identical, so one set of dims covers both). If the table instead uses foreign keys to nut or washer tables rather than raw dimensions, you would insert the appropriate IDs. The structure can vary; the key is that after this, Advance Steel knows: for a DIN 6914 bolt of Ø16 with set Na2W, use a nut of \~13 mm thick & 24 AF, and washers of 4 mm thick & 34 mm OD (two pieces). Without this data, the bolt might appear in the dialog but could fail to display nut/washer or cause errors in certain functions (like clash check, BOM, etc.).

   *Tip:* If you’re unsure of the values or the exact schema, a quick way is to find a similar diameter in the same standard from the existing data. For example, if M20 DIN 6914 is present in the default database, copy its SetNutsBolts entry and adjust the diameter and known dims for M16. This ensures you don’t miss any fields.

7. **(Optional) AutoLength Entries:** If you want Advance Steel to automatically choose the new 70 mm length for appropriate situations, update the **AutoLength** table for this bolt. If this bolt type already exists (except for the new length) and was auto-sized before, you might extend an existing range. If it’s a brand new BoltDefinition, you should add a series of ranges covering from the minimum grip to the max. For a single new length addition, consider where that length fits. For example, say previously the maximum length for M16 in that standard was 60 mm handling up to a certain grip, and after that it jumped to 80 mm. Now that 70 mm exists, you’d add or modify a range so that intermediate grips use the 70 mm instead of jumping from 60 to 80. The entries might look like (values illustrative):

   ```sql
   -- Example AutoLength rules for M16 DIN 6914 (BoltDefId = NewBoltDefID):
   INSERT INTO [AutoLength] (BoltDefId, GripMin, GripMax, Length) VALUES (<NewBoltDefID>, 0.0, 12.0, 20);
   INSERT INTO [AutoLength] (BoltDefId, GripMin, GripMax, Length) VALUES (<NewBoltDefID>, 12.0, 22.0, 30);
   ...
   INSERT INTO [AutoLength] (BoltDefId, GripMin, GripMax, Length) VALUES (<NewBoltDefID>, 50.0, 60.0, 60);
   INSERT INTO [AutoLength] (BoltDefId, GripMin, GripMax, Length) VALUES (<NewBoltDefID>, 60.0, 70.0, 70);
   INSERT INTO [AutoLength] (BoltDefId, GripMin, GripMax, Length) VALUES (<NewBoltDefID>, 70.0, 80.0, 80);
   ...
   ```

   The above shows how a 70 mm bolt could fill the gap between 60 and 80 mm. In practice, the ranges should be continuous and cover from 0 up to the maximum needed grip. If creating these from scratch, refer to a similar bolt standard’s AutoLength entries. This can be a lot of data (dozens of rows) – for bulk entry, consider using a script or Excel as mentioned in the best practices. If you choose not to do this now, the bolt will still be available but Advance Steel won’t automatically pick the 70 mm length on its own (the user would have to manually select it in the bolt dialog). It’s acceptable to skip AutoLength for custom sizes that are uncommon or if you always explicitly set the length, but documenting this is wise to avoid confusion.

8. **Finalize and Test:** After all inserts are done, double-check each table for the new entries: BoltDefinition (new bolt type present), SetBolts (new length present, linked by correct BoltDefId), SetOfBolts (new link present), SetNutsBolts (entry present for that diameter & set), and any optional ones like AutoLength. Also verify that no required field is left NULL improperly. Once satisfied, **save/commit the changes**. If using SSMS, the inserts are executed directly; if using your application’s SQL interface, ensure it commits the transaction.

   Now, to see the results in Advance Steel, you have a couple of options:

   * If you detached the database to edit it, re-attach it or place the MDF back in the correct folder. Launch Advance Steel.
   * **Update Defaults:** In Advance Steel, go to the Home tab → **Management Tools** → click **Update Defaults** (or use the command `_AstMgmUpdateValues`). This prompts Advance Steel to reload the database content into its internal caches. If you skip this and Advance Steel was already running, your new data might not be recognized immediately. Always update defaults or restart Advance Steel after a manual DB edit.
   * Open the **Bolt Editor** (in Management Tools or by placing a bolt in a model and checking the properties) and verify the new entry appears. For example, in Management Tools go to the Bolts category, find the DIN standard, and check if M16 has a 70 mm length listed. Also verify that selecting that assembly (Na2W) shows a nut and two washers in the preview. If something is missing (e.g., no nut appears), it points to an issue with the SetNutsBolts data or Standard-nut mapping.

9. **Sample Confirmation:** Try placing a bolt in a model with the new size. Use the Advance Steel modeling tool for bolts, select standard DIN 6914 (if that’s how it’s labeled in the dropdown), diameter 16, and see if 70 mm is available in the length list. Place it with the assembly (it should default to Na2W if we set that as default; if not, manually select Na2W). Ensure the bolt, nut, and washers all appear correctly and that the bill of materials reports the correct name and weight. This is the ultimate test that all necessary data was added.

Throughout this process, maintain a log of the IDs and values you inserted. If multiple tables were updated via an automated script, it’s good to cross-verify counts (for instance, if you added 1 BoltDefinition, 1 SetBolts, 1 SetOfBolts, etc., you can run SELECT COUNT before and after to ensure changes are as expected).

## Best Practices for Data Integrity and Maintenance

Adding custom data to the AstorBase database can be powerful but comes with responsibility to maintain data integrity. Here are best practices and tips to ensure your modifications don’t break Advance Steel’s functionality:

* **Always Backup Before and After Changes:** This cannot be stressed enough. **Comprehensively backup** the AstorBase.mdf (and its .ldf) before making changes. If something goes wrong, you can restore these files to get back to a working state. It’s wise to also backup after you’ve successfully added the new bolt, in case you need to migrate it or revert further changes later. Keep a versioned archive of your AstorBase as you customize it.

* **Work with the Database Offline:** Close Advance Steel while editing the database. The program caches a lot of data on startup; if it’s open, it might lock the file or overwrite your edits when it closes. Make your edits with Advance Steel shut down, then use Update Defaults or restart AS to load the changes.

* **Use the Correct IDs and Relationships:** When inserting new rows, let SQL Server generate the primary keys if the tables use identity (autoincrement). For example, BoltDefinition ID will auto-increment when you INSERT (unless the schema doesn’t use identity; all indications are it does). Capture that ID for use in child records (SetBolts, SetOfBolts, etc.). If identity insert is off, do not guess IDs or reuse an existing ID – this will cause collisions or overwriting of data. Always use unique keys.

  For foreign keys, use valid existing IDs (e.g., StandardId, StrengthClassId, SetId, AuthorId). Double-check each foreign key value before inserting. If a required reference is missing, create it *before* creating the dependent record. The insertion steps above reflect this (standard and grade first, then bolt, then lengths, etc.). Following the correct sequence avoids referential integrity errors. After all inserts, you can run sanity checks such as: ensure every new SetBolts.BoltDefId points to a BoltDefinition that exists, every SetOfBolts.SetId points to a Sets entry, etc. This can be done with LEFT JOIN queries or the tool you build (for example, a “Validate Data” function that checks for any foreign key mismatches, similar to the orphan check in the provided code snippet).

* **Fill All Required Fields:** Be mindful of NOT NULL columns. If a field must not be null, provide a reasonable value. For instance, if Weight is required in SetBolts, don’t leave it null – put 0 if unknown (and update later). If the Name in BoltDefinition is required (it is), make sure it’s unique enough to identify the bolt. Some fields might allow nulls but are still important (e.g., if a “Comment” or “Note” field is blank it’s fine, but missing a crucial dimension is not). The best practice is to mirror how official entries are populated. When unsure, open the Management Tools **Table Editor** on that table (you can do this read-only without writing changes) and observe the columns and typical values.

* **Maintain Consistency in Units and Conventions:** AstorBase uses consistent units (generally mm for dimensions, and I suspect kg for weight). Input your data in the same units. Also follow naming conventions. For example, if all metric bolt diameters are stored as whole numbers (16.0) do that; if weights are in kg to three decimals, do similarly. Consistency prevents confusion when others look at the data or when you upgrade to a new version (the migration expects things in a certain way).

* **Manage Unique Constraints:** Some tables might have unique constraints beyond the primary key. For example, Standard names might need to be unique (no two standards with the same Name), or there might be a unique composite index on (StandardId, Diameter, SetId) in SetNutsBolts to prevent duplicate entries for the same scenario. Be careful not to insert duplicates. If you accidentally insert a duplicate (say you inserted a Standard that actually already existed under a slightly different name), you might end up with two standards referencing the same norm – which could confuse things. It’s better to reuse existing where possible. For our example, if “DIN 6914” standard was in the DB under a generic “DIN” entry or something, using that would have been preferable to adding a redundant entry.

* **Author and Source Attribution:** As mentioned, use the Authors table properly. It’s good practice to add an Author entry for your company or yourself (if not already present) and use that ID for custom rows. This doesn’t affect functionality directly, but it’s very useful for tracking. For instance, Autodesk’s migration tools can carry over custom content by filtering on Author (so it knows what wasn’t out-of-the-box). In a multi-user environment, having the author set to “Company XYZ” can alert others that the bolt was custom. The Authors table typically also has an “IsSystem” or similar flag for built-in entries, so mark your custom author accordingly if needed.

* **Use the Management Tools UI for Reference:** Even though the goal is to simplify adding/editing bolts via your custom app, it’s invaluable to use the Advance Steel **Management Tools** interface to verify and sometimes initiate changes. The Management Tools bolt editor ensures all internal rules are applied. For complex tasks (like adding an entirely new bolt standard or altering assembly codes), consider doing one entry through the UI to see which tables get affected. You don’t have to do every entry with the UI (that’s what your app is for), but using it as a guide can prevent mistakes. Additionally, after you insert data via SQL, opening the same bolt in Management Tools is a good test – if Management Tools can read and display your new bolt correctly on all its tabs (Parameters, Set, Bolts, Holes), then you’ve likely added all the necessary info. If something is blank or throws an error in the UI, that indicates missing data.

* **Beware of Redundant Data Entry:** One thing you may notice is that Advance Steel’s database can be quite redundant – the same values might be repeated across tables (for example, the bolt diameter appears in BoltDefinition, and again in SetNutsBolts as a field). This is historical and for performance reasons. It means when you add a new item, you might have to enter the same value in multiple places. Our process above did that (16 mm in BoltDefinition and again in SetNutsBolts). Always double-check that these redundant fields match perfectly to avoid any inconsistency. If, for instance, you put 15.9 in one place and 16.0 in another, it could cause issues with lookups.

* **Maintain Data Integrity on Updates/Deletes:** If you later edit or remove entries, do so consistently. For example, if you decided to remove a custom bolt, remove its BoltDefinition and all related SetBolts, SetOfBolts, AutoLength, etc., to avoid orphaned data. Conversely, if you modify a bolt’s standard or diameter, update all related tables. (Your custom application could include safeguards – for example, if changing a BoltDefinition’s diameter, automatically update SetNutsBolts and SetBolts entries to match.)

* **Monitor for Application Updates:** When Autodesk releases new versions or service packs, they sometimes adjust database schemas. Keep track of your custom changes so you can reapply or migrate them. Advance Steel provides a **Content Migration Tool** that helps bring custom database content forward to a new version. This tool typically looks at Authors and known tables to copy over your additions. By adhering to the standard way of inserting data (and using the Authors table), you increase the chances that the migration tool will seamlessly carry your custom bolts into the next version. Still, always backup and manually verify after migration.

* **Test Thoroughly:** After adding a new bolt, test it in various contexts:

  * Place it manually in a model, ensure it behaves like existing bolts (appears in BOMs, the nut orientation is correct, etc.).
  * Test it in automatic connections (if you use connection templates that auto-select bolts) to see if it’s picked up.
  * Generate a drawing with a bolt list to see that the new bolt’s description and weight appear correctly.
  * If the bolt is meant for certain connections (e.g., an anchor bolt in a baseplate), test those as well. Unexpected issues can sometimes arise, for example if a connection hard-codes something about available bolt lengths or expects certain standards – but generally if the data is there, Advance Steel will use it.

* **Be Mindful of Regional Settings and Formats:** A small but notable “gotcha” – if you are dealing with imperial bolts or working in a locale that uses commas for decimals, the Management Tools might behave differently. Autodesk has noted that when editing bolts with imperial units, you should temporarily set the decimal symbol to a dot “.” in Windows regional settings. This mainly affects the UI input, but if your application is writing to the database directly, just ensure you use the correct numeric formats (the database likely expects a dot as decimal separator regardless of locale).

* **Undocumented Behaviors:** There are a few quirks reported by users in forums. For instance, one user found that they couldn’t change the nut code via the bolt editor UI for a new bolt – meaning the UI might not expose all fields (the solution in such cases is exactly what you’re doing: edit the database directly to set the desired values). Another known issue is that forgetting to hit “Update Defaults” can cause new bolts to not appear at all – always do this after a change. Also, be aware of performance: Adding a large number of bolts (say you add 1000 new length entries) can slightly impact the time it takes Advance Steel to load the databases on startup or to open the bolt dialog. This isn’t a reason not to add them, but just a consideration (the effect is usually minor unless the database becomes extremely large).

* **Bulk Editing Tips:** If you plan on adding many entries (e.g., a whole new series of bolts), prepare and test a smaller subset first. Use tools like Excel to generate SQL insert statements (this is a common approach given the volume of data). For example, you can drag formulas to list lengths, calculate weights, etc., then have a formula concatenate into SQL rows. Your custom GUI might also allow importing from CSV which can then be turned into multiple inserts. The key is to ensure each required table is populated. Some users have automated adding bolts by writing Python scripts to loop through sizes and call SQL—this reduces manual errors and ensures consistency, which is exactly the kind of efficiency your application can deliver.

* **Maintain a Change Log:** Document the changes you make to the database – which tables and how many records were added or modified. This log will help in troubleshooting and in migrating changes to future versions. It’s easy to forget a step months later; a spreadsheet or text log listing “Added M16x70 to DIN 6914: new BoltDef ID=1234, 1 SetBolts, 1 SetOfBolts, etc.” will be very helpful if something isn’t working or when another person needs to understand the customizations.

* **Recovery Plan:** If something goes wrong (e.g., you realize bolts are not showing up properly, or Advance Steel throws errors when opening the bolt dialog), be ready to revert using your backup. You can then analyze what went wrong (for example, maybe a typo in a Standard name or a missing SetNutsBolts entry). Common issues include forgetting a SetOfBolts or SetNutsBolts entry – these typically manifest as a bolt with missing assemblies or missing nuts. Another failure could be violating a constraint – for instance, if you accidentally used a duplicate primary key, the insert might not have actually succeeded. By reviewing each table, you can usually spot what’s missing.

Finally, remember that while direct DB editing is powerful, Autodesk’s official stance would be to use the Management Tools for safety. You are essentially reverse-engineering their data model, which is fine (especially for a power-user or developer), just keep in mind that future updates might tweak things. Always test your approach on a sample database before applying to your production one.

## Backup and Restore Procedure

Maintaining backups was mentioned several times – here we consolidate the steps to backup and (if needed) restore the AstorBase database:

* **Creating a Backup:** The AstorBase.mdf file (and its .ldf log) are typically found in the program data directory (e.g., `C:\ProgramData\Autodesk\Advance Steel 2025\USA\Steel\Data\AstorBase.mdf` for Advance Steel 2025 US edition, path will vary by version and locale). To backup, ensure no process is using the file (close Advance Steel completely). Then simply copy the MDF and LDF files to a safe location (another folder or a backup drive). You may zip them and note the date and any relevant notes (like “before adding M16x70 DIN bolt”). It’s a good idea to also backup related databases (AstorProfiles, etc.) if you plan to modify them, but for just bolts, AstorBase is the main one. Frequent, versioned backups are the cornerstone of safe customization.

* **Restoring from Backup:** If you need to revert to a backup, again close Advance Steel. There are two ways:

  1. **File Replace Method:** Locate the current AstorBase.mdf (and .ldf) in the Data folder, move them out (or rename them), and copy the backup MDF and LDF in. Make sure the file names match exactly what Advance Steel expects (AstorBase.mdf, AstorBase\_###.ldf – sometimes the log file might have a suffix, ensure to carry that name). When you restart Advance Steel, it will use the restored database. If the log file is missing or out-of-date, SQL LocalDB might rebuild it; usually copying both files is safest.
  2. **Detach/Attach Method (via SQL tools):** If you are comfortable with SQL Server Management Studio, you can detach the current database and attach the backup. For LocalDB, you might connect to `(LocalDB)\MSSQLLocalDB` and do `sp_detach_db 'AstorBase'`, then replace files, then `sp_attach_db`. This is more advanced but avoids file permission issues. Ensure the user account has read/write permissions on the files when attaching.

* **Verification After Restore:** Launch Advance Steel and open Management Tools to ensure the data is as expected (either the old state is back, or the new data is present if you restored a backup you made after adding the bolt). Check a known bolt to confirm things look normal.

* **Version Control for Database:** Consider treating the database like code – keep copies of the MDF for each major change. Some users even use scripts to reapply changes to a fresh database when moving to a new version (like SQL insert scripts under version control). This is beyond the scope here, but since you’re developing a tool for adding bolts, you might generate logs or scripts of changes that can serve as a “patch” to apply to another database (for example, if deploying to another workstation or upgrading to next year’s version). Having these insert statements saved (like the ones we wrote) means you could quickly re-run them on a new AstorBase if needed.

By following the above steps and precautions, you can confidently extend the Advance Steel bolt database with new sizes or types. Your standalone application can streamline this process for end-users, but under the hood it will need to perform the equivalent of the steps outlined (inserting into all the right tables). With a solid understanding of the AstorBase schema, you’ll avoid breaking constraints and ensure that Advance Steel recognizes and uses your new bolt assemblies just as if they were native content. Always test thoroughly and keep those backups handy. Good luck with your custom bolt management application!

**Sources:**

* Autodesk Advance Steel 2025 Documentation and Community Feedback – Bolt customization and database schema. These sources detail the role of key tables (BoltDefinition, SetBolts, Standard, etc.), the need to update defaults after editing, and emphasize backup and integrity checks.
