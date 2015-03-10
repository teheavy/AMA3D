SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `AMA3D` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `AMA3D` ;

-- -----------------------------------------------------
-- Table `AMA3D`.`Topology`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`Topology` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Topology` (
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
    REFERENCES `AMA3D`.`Domain` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`Domain`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`Domain` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Domain` (
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
    REFERENCES `AMA3D`.`Topology` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`Peptide`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`Peptide` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Peptide` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(20) NULL,
  `Type` ENUM('ASY', 'BIO', 'SYM') NOT NULL COMMENT 'ENUM(\'TOP\', \'ASY\', \'BIO\', \'SYM\') - \n\'TOP\': part of the actual domain for the topology; \'ASY\': part of asymmetric unit;  \'BIO\': part of biological unit; \'SYM\': part of symmetry generated context.',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idResidueSets_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `AMA3D`.`HeteroCompound`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`HeteroCompound` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`HeteroCompound` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `HetCode` CHAR(3) NOT NULL,
  `SeqNum` CHAR(5) NOT NULL COMMENT 'Residue number + optional insert code',
  `FullName` VARCHAR(100) NULL,
  `Type` ENUM('ASY', 'BIO', 'SYM') NOT NULL COMMENT 'ENUM(\'ASY\', \'BIO\', \'SYM\') - \n\'ASY\': part of asymmetric unit;  \'BIO\': part of biological unit; \'SYM\': part of symmetry generated context.',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `AMA3D`.`AminoAcid`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`AminoAcid` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`AminoAcid` (
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
    REFERENCES `AMA3D`.`AminoAcid` (`PreviousInSequence`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `idNextInSequence`
    FOREIGN KEY (`id`)
    REFERENCES `AMA3D`.`AminoAcid` (`PreviousInSequence`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `ModifiedID`
    FOREIGN KEY (`ModifiedID`)
    REFERENCES `AMA3D`.`HeteroCompound` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`Nh3DVersion`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`Nh3DVersion` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Nh3DVersion` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(45) NOT NULL,
  `DateCompleted` DATETIME NULL,
  `Description` VARCHAR(2000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idVersion_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `AMA3D`.`Nh3DTopologies`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`Nh3DTopologies` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Nh3DTopologies` (
  `idVersion` BIGINT UNSIGNED NOT NULL,
  `idTopology` BIGINT UNSIGNED NOT NULL,
  INDEX `idVersion_idx` (`idVersion` ASC),
  INDEX `idTopology_idx` (`idTopology` ASC),
  CONSTRAINT `idVersion`
    FOREIGN KEY (`idVersion`)
    REFERENCES `AMA3D`.`Nh3DVersion` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idTopology`
    FOREIGN KEY (`idTopology`)
    REFERENCES `AMA3D`.`Topology` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`DomainPeptides`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`DomainPeptides` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`DomainPeptides` (
  `idDomain` BIGINT UNSIGNED NOT NULL,
  `idPeptide` BIGINT UNSIGNED NOT NULL,
  INDEX `idPeptide_idx` (`idPeptide` ASC),
  INDEX `idDomain_idx` (`idDomain` ASC),
  CONSTRAINT `idDomain`
    FOREIGN KEY (`idDomain`)
    REFERENCES `AMA3D`.`Domain` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idPeptide`
    FOREIGN KEY (`idPeptide`)
    REFERENCES `AMA3D`.`Peptide` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`PeptideAminoAcids`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`PeptideAminoAcids` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`PeptideAminoAcids` (
  `idPeptide` BIGINT UNSIGNED NOT NULL,
  `idAminoAcid` BIGINT UNSIGNED NOT NULL,
  INDEX `idPeptide_idx` (`idPeptide` ASC),
  CONSTRAINT `idAminoAcid`
    FOREIGN KEY (`idAminoAcid`)
    REFERENCES `AMA3D`.`AminoAcid` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `idPeptide`
    FOREIGN KEY (`idPeptide`)
    REFERENCES `AMA3D`.`Peptide` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`NucleicAcid`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`NucleicAcid` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`NucleicAcid` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(20) NULL,
  `Type` ENUM('ASY', 'BIO', 'SYM') NOT NULL COMMENT 'ENUM(\'ASY\', \'BIO\', \'SYM\') - \n\'ASY\': part of asymmetric unit;  \'BIO\': part of biological unit; \'SYM\': part of symmetry generated context.',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idResidueSets_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `AMA3D`.`Nucleotide`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`Nucleotide` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Nucleotide` (
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
    REFERENCES `AMA3D`.`Nucleotide` (`PreviousInSequence`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `idNextInSequence`
    FOREIGN KEY (`id`)
    REFERENCES `AMA3D`.`Nucleotide` (`PreviousInSequence`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `ModifiedID`
    FOREIGN KEY (`ModifiedID`)
    REFERENCES `AMA3D`.`HeteroCompound` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`NucleicAcidNucleotides`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`NucleicAcidNucleotides` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`NucleicAcidNucleotides` (
  `idNucleicAcid` BIGINT UNSIGNED NOT NULL,
  `idNucleotide` BIGINT UNSIGNED NOT NULL,
  INDEX `idNucleicAcid_idx` (`idNucleicAcid` ASC),
  INDEX `idNucleotide_idx` (`idNucleotide` ASC),
  CONSTRAINT `idNucleicAcid`
    FOREIGN KEY (`idNucleicAcid`)
    REFERENCES `AMA3D`.`NucleicAcid` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idNucleotide`
    FOREIGN KEY (`idNucleotide`)
    REFERENCES `AMA3D`.`Nucleotide` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`DomainNucleicAcids`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`DomainNucleicAcids` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`DomainNucleicAcids` (
  `idDomain` BIGINT UNSIGNED NOT NULL,
  `idNucleicAcid` BIGINT UNSIGNED NOT NULL,
  INDEX `idDomain_idx` (`idDomain` ASC),
  INDEX `idNucleicAcid_idx` (`idNucleicAcid` ASC),
  CONSTRAINT `idDomain`
    FOREIGN KEY (`idDomain`)
    REFERENCES `AMA3D`.`Domain` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idNucleicAcid`
    FOREIGN KEY (`idNucleicAcid`)
    REFERENCES `AMA3D`.`NucleicAcid` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`DomainHeteroCompounds`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`DomainHeteroCompounds` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`DomainHeteroCompounds` (
  `idDomain` BIGINT UNSIGNED NOT NULL,
  `idHeteroCompound` BIGINT UNSIGNED NOT NULL,
  INDEX `idDomain_idx` (`idDomain` ASC),
  INDEX `idHeteroCompound_idx` (`idHeteroCompound` ASC),
  CONSTRAINT `idDomain`
    FOREIGN KEY (`idDomain`)
    REFERENCES `AMA3D`.`Domain` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idHeteroCompound`
    FOREIGN KEY (`idHeteroCompound`)
    REFERENCES `AMA3D`.`HeteroCompound` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`Atom`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`Atom` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Atom` (
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
-- Table `AMA3D`.`AminoAcidAtom`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`AminoAcidAtom` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`AminoAcidAtom` (
  `idAminoAcid` BIGINT UNSIGNED NOT NULL,
  `idAtom` BIGINT UNSIGNED NOT NULL,
  INDEX `idAminoAcid_idx` (`idAminoAcid` ASC),
  INDEX `idAtom_idx` (`idAtom` ASC),
  CONSTRAINT `idAminoAcid`
    FOREIGN KEY (`idAminoAcid`)
    REFERENCES `AMA3D`.`AminoAcid` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idAtom`
    FOREIGN KEY (`idAtom`)
    REFERENCES `AMA3D`.`Atom` (`idAtom`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`NucleotideAtom`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`NucleotideAtom` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`NucleotideAtom` (
  `idNucleotide` BIGINT UNSIGNED NOT NULL,
  `idAtom` BIGINT UNSIGNED NOT NULL,
  INDEX `idAtom_idx` (`idAtom` ASC),
  INDEX `idNucleotide_idx` (`idNucleotide` ASC),
  CONSTRAINT `idNucleotide`
    FOREIGN KEY (`idNucleotide`)
    REFERENCES `AMA3D`.`Nucleotide` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idAtom`
    FOREIGN KEY (`idAtom`)
    REFERENCES `AMA3D`.`Atom` (`idAtom`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`HeteroCompoundAtom`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`HeteroCompoundAtom` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`HeteroCompoundAtom` (
  `idHeteroCompound` BIGINT UNSIGNED NOT NULL,
  `idAtom` BIGINT UNSIGNED NOT NULL,
  INDEX `idAtom_idx` (`idAtom` ASC),
  INDEX `idHeteroCompound_idx` (`idHeteroCompound` ASC),
  CONSTRAINT `idHeteroCompound`
    FOREIGN KEY (`idHeteroCompound`)
    REFERENCES `AMA3D`.`HeteroCompound` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idAtom`
    FOREIGN KEY (`idAtom`)
    REFERENCES `AMA3D`.`Atom` (`idAtom`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`ResidueSet`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`ResidueSet` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`ResidueSet` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `SetName` VARCHAR(45) NOT NULL,
  `Density` FLOAT NULL,
  `Comment` VARCHAR(1000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idMotif_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `AMA3D`.`Neighbourhood`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`Neighbourhood` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Neighbourhood` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `MotifID` BIGINT UNSIGNED NOT NULL,
  `NeighbourhoodType` VARCHAR(45) NULL COMMENT 'Ball, Voronoi, other ... convert into enum at later time; encode parameter(s) in name',
  UNIQUE INDEX `idNeighborhood_UNIQUE` (`id` ASC),
  INDEX `MotifID_idx` (`MotifID` ASC),
  PRIMARY KEY (`id`),
  CONSTRAINT `MotifID`
    FOREIGN KEY (`MotifID`)
    REFERENCES `AMA3D`.`ResidueSet` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`MotifNeighbour`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`MotifNeighbour` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`MotifNeighbour` (
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
    REFERENCES `AMA3D`.`Neighbourhood` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `ResidueSetID`
    FOREIGN KEY (`ResidueSetID`)
    REFERENCES `AMA3D`.`ResidueSet` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`RsidueSetPeptides`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`RsidueSetPeptides` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`RsidueSetPeptides` (
  `idResidueSet` BIGINT UNSIGNED NOT NULL,
  `idPeptide` BIGINT UNSIGNED NOT NULL,
  INDEX `idPeptide_idx` (`idPeptide` ASC),
  INDEX `idMotif_idx` (`idResidueSet` ASC),
  CONSTRAINT `idResidueSet`
    FOREIGN KEY (`idResidueSet`)
    REFERENCES `AMA3D`.`ResidueSet` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idPeptide`
    FOREIGN KEY (`idPeptide`)
    REFERENCES `AMA3D`.`Peptide` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`SchematikonVersion`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`SchematikonVersion` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`SchematikonVersion` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(45) NOT NULL,
  `DateCompleted` DATETIME NULL,
  `Description` VARCHAR(2000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idVersion_UNIQUE` (`id` ASC))
;


-- -----------------------------------------------------
-- Table `AMA3D`.`SchematikonMotifs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`SchematikonMotifs` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`SchematikonMotifs` (
  `idVersion` BIGINT UNSIGNED NOT NULL,
  `idMotif` BIGINT UNSIGNED NOT NULL,
  INDEX `idVersion_idx` (`idVersion` ASC),
  INDEX `idMotif_idx` (`idMotif` ASC),
  CONSTRAINT `idVersion`
    FOREIGN KEY (`idVersion`)
    REFERENCES `AMA3D`.`SchematikonVersion` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `idMotif`
    FOREIGN KEY (`idMotif`)
    REFERENCES `AMA3D`.`ResidueSet` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
;


-- -----------------------------------------------------
-- Table `AMA3D`.`TriggeringCondition`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`TriggeringCondition` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`TriggeringCondition` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Parameters` VARCHAR(45) NULL, -- This is for load method
  `idTaskResource` INT NOT NULL,
  `idAgent` INT NOT NULL,
  `IsLast` TINYINT(1) NOT NULL,
  `Status` INT NOT NULL, -- 0 - open 1, -- in_progress
  PRIMARY KEY (`id`))
;


-- -----------------------------------------------------
-- Table `AMA3D`.`TaskResource`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`TaskResource` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`TaskResource` (
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
-- Table `AMA3D`.`Agent`
-- -----------------------------------------------------


DROP TABLE IF EXISTS `AMA3D`.`Agent` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Agent` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, 
  `RegisterTime` DATETIME NOT NULL,
  `StartTime` DATETIME DEFAULT '1000-01-01 00-00-00',
  `Status` INT DEFAULT 0, -- 0 = free, 1 = busy
  `NumTaskDone` INT NOT NULL,
  `Priority` INT NOT NULL,
  PRIMARY KEY (`id`))
;
--idParent INT NOT NULL, Figure out why we need idParent
-- -----------------------------------------------------
-- Table `AMA3D`.`Machines`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`Machines` ;

CREATE TABLE IF NOT EXISTS `AMA3D`.`Machines` (
  `idMachine` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `User` VARCHAR(45) NOT NULL,
  `Path` VARCHAR(100) NULL,
  `Host` VARCHAR(45) NOT NULL,
  `Port` INT Default NULL,
  `CPU` INT Default NULL,
  `FreeMem` INT Default NULL,
  PRIMARY KEY (`idMachine`))
;

-- -----------------------------------------------------
-- Table `AMA3D`.`Log`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AMA3D`.`LogActivity` ;
CREATE TABLE IF NOT EXISTS `AMA3D`.`LogActivity` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `AgentID` INT NOT NULL,
  `MachineID` INT NOT NULL,
  `TimeStamp` DATETIME NOT NULL,
  `Activity` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`))
;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
