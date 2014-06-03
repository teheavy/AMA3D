SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `Schematikon_2` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `Schematikon_2` ;

-- -----------------------------------------------------
-- Table `Schematikon_2`.`Topology`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Topology` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Topology` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(45) NOT NULL,
  `Source` VARCHAR(45) NULL,
  `Comment` VARCHAR(255) NULL,
  `Representative` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `Representative_idx` (`Representative` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  CONSTRAINT `Representative`
    FOREIGN KEY (`Representative`)
    REFERENCES `Schematikon_2`.`Domain` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`Domain`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Domain` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Domain` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(20) NOT NULL,
  `Comment` VARCHAR(255) NULL,
  `Topology` BIGINT UNSIGNED NOT NULL,
  `PDB_ID` CHAR(4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idComplex_UNIQUE` (`id` ASC),
  INDEX `Topology_idx` (`Topology` ASC),
  CONSTRAINT `TopologyID`
    FOREIGN KEY (`Topology`)
    REFERENCES `Schematikon_2`.`Topology` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`Peptide`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Peptide` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Peptide` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(20) NULL,
  `Type` ENUM('ASY', 'BIO', 'SYM') NOT NULL COMMENT 'ENUM(\'TOP\', \'ASY\', \'BIO\', \'SYM\') - \n\'TOP\': part of the actual domain for the topology; \'ASY\': part of asymmetric unit;  \'BIO\': part of biological unit; \'SYM\': part of symmetry generated context.',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idResidueSets_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`HeteroCompound`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`HeteroCompound` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`HeteroCompound` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `HetCode` CHAR(3) NOT NULL,
  `SeqNum` CHAR(5) NOT NULL COMMENT 'Residue number + optional insert code',
  `FullName` VARCHAR(100) NULL,
  `Type` ENUM('ASY', 'BIO', 'SYM') NOT NULL COMMENT 'ENUM(\'ASY\', \'BIO\', \'SYM\') - \n\'ASY\': part of asymmetric unit;  \'BIO\': part of biological unit; \'SYM\': part of symmetry generated context.',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`AminoAcid`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`AminoAcid` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`AminoAcid` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `AminoAcidCode` CHAR(3) NOT NULL,
  `ModifiedID` BIGINT UNSIGNED NULL COMMENT 'If not NULL, the amino acid is modified and the coordinates are stored as a HET group.',
  `SeqNum` CHAR(5) NOT NULL COMMENT 'Residue number + optional insert code',
  `PreviousInSequence` BIGINT UNSIGNED NULL,
  `NextInSequence` BIGINT UNSIGNED NULL,
  `phi` FLOAT NULL,
  `psi` FLOAT NULL,
  `omega` FLOAT NULL,
  `chi1` FLOAT NULL,
  `chi2` FLOAT NULL,
  `chi3` FLOAT NULL,
  `SASA` FLOAT NULL,
  `RelativeSASA` FLOAT NULL,
  `Stride` CHAR(1) NULL,
  `DSSP` CHAR(1) NULL,
  `Vorocode` CHAR(1) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `ModifiedID_idx` (`ModifiedID` ASC),
  CONSTRAINT `idPreviousInSequence`
    FOREIGN KEY (`id`)
    REFERENCES `Schematikon_2`.`AminoAcid` (`PreviousInSequence`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `idNextInSequence`
    FOREIGN KEY (`id`)
    REFERENCES `Schematikon_2`.`AminoAcid` (`PreviousInSequence`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `ModifiedID`
    FOREIGN KEY (`ModifiedID`)
    REFERENCES `Schematikon_2`.`HeteroCompound` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`Nh3DVersion`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Nh3DVersion` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Nh3DVersion` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(45) NOT NULL,
  `DateCompleted` DATETIME NULL,
  `Description` VARCHAR(2000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idVersion_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`Nh3DTopologies`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Nh3DTopologies` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Nh3DTopologies` (
  `idVersion` BIGINT UNSIGNED NOT NULL,
  `idTopology` BIGINT UNSIGNED NOT NULL,
  INDEX `idVersion_idx` (`idVersion` ASC),
  INDEX `idTopology_idx` (`idTopology` ASC),
  CONSTRAINT `idVersion`
    FOREIGN KEY (`idVersion`)
    REFERENCES `Schematikon_2`.`Nh3DVersion` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idTopology`
    FOREIGN KEY (`idTopology`)
    REFERENCES `Schematikon_2`.`Topology` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`DomainPeptides`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`DomainPeptides` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`DomainPeptides` (
  `idDomain` BIGINT UNSIGNED NOT NULL,
  `idPeptide` BIGINT UNSIGNED NOT NULL,
  INDEX `idPeptide_idx` (`idPeptide` ASC),
  INDEX `idDomain_idx` (`idDomain` ASC),
  CONSTRAINT `idDomain`
    FOREIGN KEY (`idDomain`)
    REFERENCES `Schematikon_2`.`Domain` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idPeptide`
    FOREIGN KEY (`idPeptide`)
    REFERENCES `Schematikon_2`.`Peptide` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`PeptideAminoAcids`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`PeptideAminoAcids` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`PeptideAminoAcids` (
  `idPeptide` BIGINT UNSIGNED NOT NULL,
  `idAminoAcid` BIGINT UNSIGNED NOT NULL,
  INDEX `idPeptide_idx` (`idPeptide` ASC),
  CONSTRAINT `idAminoAcid`
    FOREIGN KEY (`idAminoAcid`)
    REFERENCES `Schematikon_2`.`AminoAcid` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `idPeptide`
    FOREIGN KEY (`idPeptide`)
    REFERENCES `Schematikon_2`.`Peptide` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`NucleicAcid`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`NucleicAcid` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`NucleicAcid` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(20) NULL,
  `Type` ENUM('ASY', 'BIO', 'SYM') NOT NULL COMMENT 'ENUM(\'ASY\', \'BIO\', \'SYM\') - \n\'ASY\': part of asymmetric unit;  \'BIO\': part of biological unit; \'SYM\': part of symmetry generated context.',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idResidueSets_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`Nucleotide`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Nucleotide` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Nucleotide` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `NucleotideCode` CHAR(3) NOT NULL COMMENT 'As per PDB spec \' DX\' are right-aligned deoxyRNA and \'  X\' are RNA codes.',
  `SeqNum` CHAR(5) NOT NULL COMMENT 'Residue number (4) + optional insert code (1), right aligned and blank filled.',
  `ModifiedID` BIGINT UNSIGNED NULL COMMENT 'If not NULL, the nucleotide is modified and the coordinates are started as a HET group.',
  `PreviousInSequence` BIGINT UNSIGNED NULL,
  `NextInSequence` BIGINT UNSIGNED NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `ModifiedID_idx` (`ModifiedID` ASC),
  CONSTRAINT `idPreviousInSequence`
    FOREIGN KEY (`id`)
    REFERENCES `Schematikon_2`.`Nucleotide` (`PreviousInSequence`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `idNextInSequence`
    FOREIGN KEY (`id`)
    REFERENCES `Schematikon_2`.`Nucleotide` (`PreviousInSequence`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `ModifiedID`
    FOREIGN KEY (`ModifiedID`)
    REFERENCES `Schematikon_2`.`HeteroCompound` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`NucleicAcidNucleotides`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`NucleicAcidNucleotides` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`NucleicAcidNucleotides` (
  `idNucleicAcid` BIGINT UNSIGNED NOT NULL,
  `idNucleotide` BIGINT UNSIGNED NOT NULL,
  INDEX `idNucleicAcid_idx` (`idNucleicAcid` ASC),
  INDEX `idNucleotide_idx` (`idNucleotide` ASC),
  CONSTRAINT `idNucleicAcid`
    FOREIGN KEY (`idNucleicAcid`)
    REFERENCES `Schematikon_2`.`NucleicAcid` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idNucleotide`
    FOREIGN KEY (`idNucleotide`)
    REFERENCES `Schematikon_2`.`Nucleotide` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`DomainNucleicAcids`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`DomainNucleicAcids` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`DomainNucleicAcids` (
  `idDomain` BIGINT UNSIGNED NOT NULL,
  `idNucleicAcid` BIGINT UNSIGNED NOT NULL,
  INDEX `idDomain_idx` (`idDomain` ASC),
  INDEX `idNucleicAcid_idx` (`idNucleicAcid` ASC),
  CONSTRAINT `idDomain`
    FOREIGN KEY (`idDomain`)
    REFERENCES `Schematikon_2`.`Domain` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idNucleicAcid`
    FOREIGN KEY (`idNucleicAcid`)
    REFERENCES `Schematikon_2`.`NucleicAcid` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`DomainHeteroCompounds`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`DomainHeteroCompounds` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`DomainHeteroCompounds` (
  `idDomain` BIGINT UNSIGNED NOT NULL,
  `idHeteroCompound` BIGINT UNSIGNED NOT NULL,
  INDEX `idDomain_idx` (`idDomain` ASC),
  INDEX `idHeteroCompound_idx` (`idHeteroCompound` ASC),
  CONSTRAINT `idDomain`
    FOREIGN KEY (`idDomain`)
    REFERENCES `Schematikon_2`.`Domain` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idHeteroCompound`
    FOREIGN KEY (`idHeteroCompound`)
    REFERENCES `Schematikon_2`.`HeteroCompound` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`Atom`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Atom` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Atom` (
  `idAtom` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `SerialNumber` MEDIUMINT UNSIGNED NOT NULL,
  `Name` CHAR(4) NOT NULL,
  `AltLoc` CHAR(1) NOT NULL COMMENT 'Blank if none',
  `ResName` CHAR(3) NOT NULL,
  `Chain` CHAR(1) NOT NULL COMMENT '\'A\' if none',
  `SeqNum` CHAR(5) NOT NULL COMMENT 'Residue number + optional insert code',
  `X` FLOAT NOT NULL,
  `Y` FLOAT NOT NULL,
  `Z` FLOAT NOT NULL,
  `Occ` FLOAT NOT NULL,
  `B` FLOAT NOT NULL,
  PRIMARY KEY (`idAtom`),
  UNIQUE INDEX `idAtom_UNIQUE` (`idAtom` ASC))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`AminoAcidAtom`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`AminoAcidAtom` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`AminoAcidAtom` (
  `idAminoAcid` BIGINT UNSIGNED NOT NULL,
  `idAtom` BIGINT UNSIGNED NOT NULL,
  INDEX `idAminoAcid_idx` (`idAminoAcid` ASC),
  INDEX `idAtom_idx` (`idAtom` ASC),
  CONSTRAINT `idAminoAcid`
    FOREIGN KEY (`idAminoAcid`)
    REFERENCES `Schematikon_2`.`AminoAcid` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idAtom`
    FOREIGN KEY (`idAtom`)
    REFERENCES `Schematikon_2`.`Atom` (`idAtom`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`NucleotideAtom`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`NucleotideAtom` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`NucleotideAtom` (
  `idNucleotide` BIGINT UNSIGNED NOT NULL,
  `idAtom` BIGINT UNSIGNED NOT NULL,
  INDEX `idAtom_idx` (`idAtom` ASC),
  INDEX `idNucleotide_idx` (`idNucleotide` ASC),
  CONSTRAINT `idNucleotide`
    FOREIGN KEY (`idNucleotide`)
    REFERENCES `Schematikon_2`.`Nucleotide` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idAtom`
    FOREIGN KEY (`idAtom`)
    REFERENCES `Schematikon_2`.`Atom` (`idAtom`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`HeteroCompoundAtom`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`HeteroCompoundAtom` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`HeteroCompoundAtom` (
  `idHeteroCompound` BIGINT UNSIGNED NOT NULL,
  `idAtom` BIGINT UNSIGNED NOT NULL,
  INDEX `idAtom_idx` (`idAtom` ASC),
  INDEX `idHeteroCompound_idx` (`idHeteroCompound` ASC),
  CONSTRAINT `idHeteroCompound`
    FOREIGN KEY (`idHeteroCompound`)
    REFERENCES `Schematikon_2`.`HeteroCompound` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idAtom`
    FOREIGN KEY (`idAtom`)
    REFERENCES `Schematikon_2`.`Atom` (`idAtom`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`ResidueSet`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`ResidueSet` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`ResidueSet` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `SetName` VARCHAR(45) NOT NULL,
  `Density` FLOAT NULL,
  `Comment` VARCHAR(1000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idMotif_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`Neighbourhood`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Neighbourhood` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Neighbourhood` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `MotifID` BIGINT UNSIGNED NOT NULL,
  `NeighbourhoodType` VARCHAR(45) NULL COMMENT 'Ball, Voronoi, other ... convert into enum at later time; encode parameter(s) in name',
  UNIQUE INDEX `idNeighborhood_UNIQUE` (`id` ASC),
  INDEX `MotifID_idx` (`MotifID` ASC),
  PRIMARY KEY (`id`),
  CONSTRAINT `MotifID`
    FOREIGN KEY (`MotifID`)
    REFERENCES `Schematikon_2`.`ResidueSet` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`MotifNeighbour`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`MotifNeighbour` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`MotifNeighbour` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `ResidueSetID` BIGINT UNSIGNED NOT NULL,
  `NeighbourhoodID` BIGINT UNSIGNED NOT NULL,
  `Density` FLOAT NULL,
  `RMSD` FLOAT UNSIGNED NOT NULL,
  `RotMat_00` FLOAT NOT NULL,
  `RotMat_01` FLOAT NOT NULL,
  `RotMat_02` FLOAT NOT NULL,
  `RotMat_10` FLOAT NOT NULL,
  `RotMat_11` FLOAT NOT NULL,
  `RotMat_12` FLOAT NOT NULL,
  `RotMat_20` FLOAT NOT NULL,
  `RotMat_21` FLOAT NOT NULL,
  `RotMat_22` FLOAT NOT NULL,
  `TraVec_X` FLOAT NOT NULL,
  `TraVec_Y` FLOAT NOT NULL,
  `TraVec_Z` FLOAT NOT NULL,
  `Comment` VARCHAR(1000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idMotif_UNIQUE` (`id` ASC),
  INDEX `NeighbourhoodID_idx` (`NeighbourhoodID` ASC),
  INDEX `ResidueSetID_idx` (`ResidueSetID` ASC),
  CONSTRAINT `NeighbourhoodID`
    FOREIGN KEY (`NeighbourhoodID`)
    REFERENCES `Schematikon_2`.`Neighbourhood` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `ResidueSetID`
    FOREIGN KEY (`ResidueSetID`)
    REFERENCES `Schematikon_2`.`ResidueSet` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`RsidueSetPeptides`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`RsidueSetPeptides` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`RsidueSetPeptides` (
  `idResidueSet` BIGINT UNSIGNED NOT NULL,
  `idPeptide` BIGINT UNSIGNED NOT NULL,
  INDEX `idPeptide_idx` (`idPeptide` ASC),
  INDEX `idMotif_idx` (`idResidueSet` ASC),
  CONSTRAINT `idResidueSet`
    FOREIGN KEY (`idResidueSet`)
    REFERENCES `Schematikon_2`.`ResidueSet` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idPeptide`
    FOREIGN KEY (`idPeptide`)
    REFERENCES `Schematikon_2`.`Peptide` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`SchematikonVersion`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`SchematikonVersion` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`SchematikonVersion` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(45) NOT NULL,
  `DateCompleted` DATETIME NULL,
  `Description` VARCHAR(2000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idVersion_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`SchematikonMotifs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`SchematikonMotifs` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`SchematikonMotifs` (
  `idVersion` BIGINT UNSIGNED NOT NULL,
  `idMotif` BIGINT UNSIGNED NOT NULL,
  INDEX `idVersion_idx` (`idVersion` ASC),
  INDEX `idMotif_idx` (`idMotif` ASC),
  CONSTRAINT `idVersion`
    FOREIGN KEY (`idVersion`)
    REFERENCES `Schematikon_2`.`SchematikonVersion` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idMotif`
    FOREIGN KEY (`idMotif`)
    REFERENCES `Schematikon_2`.`ResidueSet` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`TriggeringCondition`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`TriggeringCondition` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`TriggeringCondition` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Parameters` VARCHAR(45) NULL,
  `idTaskResource` INT NOT NULL,
  `idAgent` INT NOT NULL,
  `IsLast` TINYINT(1) NOT NULL,
  `Status` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`TaskResource`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`TaskResource` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`TaskResource` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Codepath` VARCHAR(45) NOT NULL,
  `Version` VARCHAR(45) NOT NULL,
  `CPU` VARCHAR(45) NULL,
  `RAM` VARCHAR(45) NULL,
  `numTimesExecuted` INT NULL,
  `OpSequence` VARCHAR(45) NULL,
  `Wallclock` VARCHAR(45) NULL,
  `Program` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`Agent`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Agent` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Agent` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `idParent` INT NOT NULL,
  `RegisterTime` DATETIME NOT NULL,
  `StartTime` DATETIME NOT NULL,
  `Status` INT NOT NULL,
  `NumTaskDone` INT NOT NULL,
  PRIMARY KEY (`id`))
;


-- -----------------------------------------------------
-- Table `Schematikon_2`.`Machines`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Schematikon_2`.`Machines` ;

CREATE TABLE IF NOT EXISTS `Schematikon_2`.`Machines` (
  `idMachine` BIGINT UNSIGNED NOT NULL,
  `User` VARCHAR(45) NOT NULL,
  `Path` VARCHAR(100) NULL,
  `Host` VARCHAR(45) NOT NULL,
  `Port` INT NOT NULL,
  `CPU` INT NOT NULL,
  `FreeMem` INT NOT NULL,
  PRIMARY KEY (`idMachine`))
;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
