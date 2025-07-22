// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EthicalAI {
    address public owner;

    struct ComplianceRecord {
        uint id;
        string summary;        // A brief summary of the compliance report
        string hash;           // A hash of the full compliance document
        uint256 timestamp;     // Timestamp of when the record was added
        string metadata;       // Additional metadata or notes about the compliance
    }

    ComplianceRecord[] public records;

    event ComplianceRecordAdded(uint recordId, string summary, string hash, uint256 timestamp, string metadata);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    // Add a new compliance record
    function addComplianceRecord(
        string memory _summary,
        string memory _hash,
        string memory _metadata
    ) public onlyOwner {
        uint recordId = records.length;
        uint256 currentTimestamp = block.timestamp; // Get the current timestamp
        records.push(ComplianceRecord(recordId, _summary, _hash, currentTimestamp, _metadata));
        emit ComplianceRecordAdded(recordId, _summary, _hash, currentTimestamp, _metadata);
    }

    // Retrieve a compliance record by ID
    function getComplianceRecord(uint _recordId) public view returns (
        uint,
        string memory,
        string memory,
        uint256,
        string memory
    ) {
        require(_recordId < records.length, "Record does not exist");
        ComplianceRecord storage record = records[_recordId];
        return (record.id, record.summary, record.hash, record.timestamp, record.metadata);
    }

    // Get the total number of compliance records
    function getTotalRecords() public view returns (uint) {
        return records.length;
    }
}